/* Headless mGBA harness for the Orleans playtest bot.
 * Line protocol on stdin; one reply line per command on stdout ("OK ..." or "ERR ...").
 * Build: tools/playtest/build_harness.sh       Run: harness ROM.gba [unix_time]
 * Commands:
 *   frames N | press KEYS HOLD [RELEASE] | hold KEYS | release
 *   read8|read16|read32 ADDR | readblock ADDR LEN | write8|write16|write32 ADDR VAL
 *   shot PATH.ppm | hash | nonblack (count of non-black pixels) | savestate PATH | loadstate PATH | reset | rtc UNIXSECS
 *   call ADDR [r0 r1 r2 r3]   (calls a ROM function, thumb if ADDR odd; replies with r0)
 *   safepoint ADDR  (function entry used as the clean point for call; set once after boot)
 *   framecount | quit
 * KEYS: names joined by '+': A B SELECT START RIGHT LEFT UP DOWN R L (or NONE).
 */
#include <mgba/core/core.h>
#include <mgba/core/config.h>
#include <mgba/core/serialize.h>
#include <mgba/gba/core.h>
#include <mgba/gba/interface.h>
#include <mgba/internal/arm/arm.h>
#include <mgba/core/log.h>
#include <mgba-util/vfs.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <stdint.h>

static void quietLog(struct mLogger *l, int category, enum mLogLevel level, const char *fmt, va_list args) {
    (void) l;
    /* only real faults reach stderr (the bot keeps them in harness.log): fatal, error, game error */
    if (level & (mLOG_FATAL | mLOG_ERROR | mLOG_GAME_ERROR)) {
        fprintf(stderr, "[%s] ", mLogCategoryName(category));
        vfprintf(stderr, fmt, args);
        fputc('\n', stderr);
    }
}
static struct mLogger quietLogger = { .log = quietLog };
static struct mLogFilter quietFilter;
static struct mCore *core;
static color_t *vbuf;
static unsigned W, H;
static uint32_t keys_held;
static uint64_t total_frames;
static char *romPath;

static int keyBit(const char *n) {
    static const char *names[] = {"A","B","SELECT","START","RIGHT","LEFT","UP","DOWN","R","L"};
    for (int i = 0; i < 10; i++) if (!strcasecmp(n, names[i])) return i;
    return -1;
}
static int parseKeys(char *s, uint32_t *out) {
    uint32_t m = 0;
    if (strcasecmp(s, "NONE") == 0) { *out = 0; return 0; }
    for (char *t = strtok(s, "+,"); t; t = strtok(NULL, "+,")) {
        int b = keyBit(t);
        if (b < 0) return -1;
        m |= 1u << b;
    }
    *out = m;
    return 0;
}
static void runFrames(unsigned n) {
    for (unsigned i = 0; i < n; i++) { core->setKeys(core, keys_held); core->runFrame(core); total_frames++; }
}
static int bootCore(void) {
    core = mCoreFind(romPath);
    if (!core) return -1;
    core->init(core);
    mCoreInitConfig(core, NULL);
    W = 240; H = 160;
    vbuf = calloc(W * H, sizeof(color_t));
    core->setVideoBuffer(core, vbuf, W);
    core->setAudioBufferSize(core, 1024);
    if (!mCoreLoadFile(core, romPath)) return -2;
    struct VFile *sav = VFileMemChunk(NULL, 0);
    core->loadSave(core, sav);
    total_frames = 0;
    return 0;
}
static void setRtc(int64_t secs) {
    core->rtc.override = RTC_FAKE_EPOCH;
    core->rtc.value = secs * 1000;
}
static uint32_t shotHash(void) {
    uint32_t h = 2166136261u;
    for (unsigned i = 0; i < W * H; i++) { h ^= vbuf[i]; h *= 16777619u; }
    return h;
}
static unsigned nonBlack(void) {
    unsigned n = 0;
    for (unsigned i = 0; i < W * H; i++) if (vbuf[i] & 0xFFFFFF) n++;
    return n;
}
static int shot(const char *path) {
    FILE *f = fopen(path, "wb");
    if (!f) return -1;
    fprintf(f, "P6\n%u %u\n255\n", W, H);
    for (unsigned i = 0; i < W * H; i++) {
        color_t c = vbuf[i];
        /* mGBA default color_t is XBGR8: R in low byte */
        unsigned char px[3] = {c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF};
        fwrite(px, 1, 3, f);
    }
    fclose(f);
    return 0;
}
static int saveState(const char *path) {
    size_t sz = core->stateSize(core);
    void *buf = malloc(sz);
    if (!core->saveState(core, buf)) { free(buf); return -1; }
    FILE *f = fopen(path, "wb");
    if (!f) { free(buf); return -2; }
    fwrite(buf, 1, sz, f); fclose(f); free(buf);
    return 0;
}
static int loadState(const char *path) {
    size_t sz = core->stateSize(core);
    void *buf = malloc(sz);
    FILE *f = fopen(path, "rb");
    if (!f) { free(buf); return -2; }
    size_t got = fread(buf, 1, sz, f); fclose(f);
    int ok = (got == sz) && core->loadState(core, buf);
    free(buf);
    return ok ? 0 : -1;
}

#define TRAP 0x09FFFF00u
static uint32_t safePoint; /* function entry hit once per main-loop iteration; calls are made from there */

/* Run ROM function at addr (thumb if odd). To keep emulator state sane the call is made from a clean point:
 * we step until the game reaches safePoint (an entry that runs once per frame in AgbMainLoop), run the function with
 * LR trapped, and restore every register so the game resumes as if nothing happened. */
static int callFn(uint32_t addr, uint32_t a0, uint32_t a1, uint32_t a2, uint32_t a3, uint32_t *ret) {
    struct ARMCore *cpu = core->cpu;
    if (safePoint) {
        long guard = 0;
        int hit = 0;
        while (guard++ < 6000000L) {
            core->step(core);
            if ((uint32_t) cpu->gprs[15] == safePoint + 2 && cpu->cpsr.t && (cpu->cpsr.packed & 0x1F) == 0x1F) { hit = 1; break; }
        }
        if (!hit) return -1;
    } else {
        int guard = 0;
        while ((cpu->cpsr.packed & 0x1F) != 0x1F && guard++ < 200000) core->step(core);
        if ((cpu->cpsr.packed & 0x1F) != 0x1F) return -1;
    }
    int32_t saved[16]; for (int i = 0; i < 16; i++) saved[i] = cpu->gprs[i];
    union PSR savedPsr = cpu->cpsr;
    int savedHalt = cpu->halted;
    cpu->halted = 0;
    uint32_t v;
    v = a0; core->writeRegister(core, "r0", &v);
    v = a1; core->writeRegister(core, "r1", &v);
    v = a2; core->writeRegister(core, "r2", &v);
    v = a3; core->writeRegister(core, "r3", &v);
    v = TRAP | 1; core->writeRegister(core, "lr", &v);
    union PSR p = cpu->cpsr;
    p.t = (addr & 1) ? 1 : 0;
    uint32_t pk = p.packed; core->writeRegister(core, "cpsr", &pk);
    v = addr & ~1u; core->writeRegister(core, "pc", &v);
    long steps = 0; int done = 0;
    while (steps++ < 20000000L) {
        core->step(core);
        uint32_t pc = (uint32_t) cpu->gprs[15];
        if (pc >= TRAP && pc < TRAP + 16) { done = 1; break; }
    }
    if (done && ret) *ret = (uint32_t) cpu->gprs[0];
    /* restore */
    pk = savedPsr.packed; core->writeRegister(core, "cpsr", &pk);
    for (int i = 0; i < 15; i++) { uint32_t r = saved[i]; char nm[8]; snprintf(nm, 8, "r%d", i); core->writeRegister(core, nm, &r); }
    uint32_t pc = (uint32_t) saved[15];
    /* gprs[15] runs ahead of the next instruction by one fetch (+2 thumb / +4 arm); writeRegister wants the address
     * of the next instruction to execute */
    pc -= savedPsr.t ? 2 : 4;
    core->writeRegister(core, "pc", &pc);
    cpu->halted = savedHalt;
    if (getenv("HARNESS_DEBUG")) {
        fprintf(stderr, "[callFn] saved pc=%08x sp=%08x lr=%08x cpsr=%08x | now pc=%08x sp=%08x lr=%08x cpsr=%08x pf0=%08x\n",
                (uint32_t) saved[15], (uint32_t) saved[13], (uint32_t) saved[14], savedPsr.packed,
                (uint32_t) cpu->gprs[15], (uint32_t) cpu->gprs[13], (uint32_t) cpu->gprs[14], cpu->cpsr.packed, (uint32_t) cpu->prefetch[0]);
    }
    return done ? 0 : -2;
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: harness ROM [unix_time]\n"); return 2; }
    romPath = argv[1];
    mLogFilterInit(&quietFilter); mLogFilterSet(&quietFilter, "gba.bios", mLOG_FATAL | mLOG_ERROR | mLOG_GAME_ERROR); mLogFilterSet(&quietFilter, "gba.memory", mLOG_FATAL | mLOG_ERROR | mLOG_GAME_ERROR); mLogFilterSet(&quietFilter, "gba.dma", mLOG_FATAL | mLOG_ERROR | mLOG_GAME_ERROR); mLogFilterSet(&quietFilter, "gba.video", mLOG_FATAL | mLOG_ERROR | mLOG_GAME_ERROR); mLogFilterSet(&quietFilter, "gba.io", mLOG_FATAL | mLOG_ERROR | mLOG_GAME_ERROR); mLogFilterSet(&quietFilter, "gba", mLOG_FATAL | mLOG_ERROR | mLOG_GAME_ERROR); mLogFilterSet(&quietFilter, "core", mLOG_FATAL | mLOG_ERROR | mLOG_GAME_ERROR); quietLogger.filter = &quietFilter; mLogSetDefaultLogger(&quietLogger);
    int r = bootCore();
    if (r) { printf("ERR boot %d\n", r); return 1; }
    int64_t t0 = argc > 2 ? atoll(argv[2]) : 1760000000LL; /* fixed default so runs reproduce */
    setRtc(t0);
    core->reset(core);
    printf("OK ready %ux%u\n", W, H); fflush(stdout);
    char line[4096];
    while (fgets(line, sizeof line, stdin)) {
        char *cmd = strtok(line, " \t\r\n");
        if (!cmd) continue;
        char *a1 = strtok(NULL, " \t\r\n"), *a2 = strtok(NULL, " \t\r\n"), *a3 = strtok(NULL, " \t\r\n"), *a4 = strtok(NULL, " \t\r\n"), *a5 = strtok(NULL, " \t\r\n");
        uint32_t k;
        if (!strcmp(cmd, "quit")) { printf("OK bye\n"); fflush(stdout); break; }
        else if (!strcmp(cmd, "frames") && a1) { runFrames(strtoul(a1, 0, 0)); printf("OK %llu\n", (unsigned long long) total_frames); }
        else if (!strcmp(cmd, "press") && a1 && a2) {
            if (parseKeys(a1, &k)) { printf("ERR badkey\n"); fflush(stdout); continue; }
            keys_held = k; runFrames(strtoul(a2, 0, 0)); keys_held = 0;
            if (a3) runFrames(strtoul(a3, 0, 0));
            printf("OK %llu\n", (unsigned long long) total_frames);
        }
        else if (!strcmp(cmd, "hold") && a1) { if (parseKeys(a1, &k)) printf("ERR badkey\n"); else { keys_held = k; printf("OK\n"); } }
        else if (!strcmp(cmd, "release")) { keys_held = 0; printf("OK\n"); }
        else if (!strcmp(cmd, "read8") && a1) printf("OK %u\n", core->busRead8(core, strtoul(a1, 0, 0)));
        else if (!strcmp(cmd, "read16") && a1) printf("OK %u\n", core->busRead16(core, strtoul(a1, 0, 0)));
        else if (!strcmp(cmd, "read32") && a1) printf("OK %u\n", core->busRead32(core, strtoul(a1, 0, 0)));
        else if (!strcmp(cmd, "readblock") && a1 && a2) {
            uint32_t ad = strtoul(a1, 0, 0), n = strtoul(a2, 0, 0);
            printf("OK ");
            for (uint32_t i = 0; i < n; i++) printf("%02x", core->busRead8(core, ad + i));
            printf("\n");
        }
        else if (!strcmp(cmd, "write8") && a1 && a2) { core->busWrite8(core, strtoul(a1, 0, 0), strtoul(a2, 0, 0)); printf("OK\n"); }
        else if (!strcmp(cmd, "write16") && a1 && a2) { core->busWrite16(core, strtoul(a1, 0, 0), strtoul(a2, 0, 0)); printf("OK\n"); }
        else if (!strcmp(cmd, "write32") && a1 && a2) { core->busWrite32(core, strtoul(a1, 0, 0), strtoul(a2, 0, 0)); printf("OK\n"); }
        else if (!strcmp(cmd, "shot") && a1) printf(shot(a1) ? "ERR shot\n" : "OK\n");
        else if (!strcmp(cmd, "nonblack")) printf("OK %u\n", nonBlack());
        else if (!strcmp(cmd, "hash")) printf("OK %08x\n", shotHash());
        else if (!strcmp(cmd, "savestate") && a1) printf(saveState(a1) ? "ERR savestate\n" : "OK\n");
        else if (!strcmp(cmd, "loadstate") && a1) printf(loadState(a1) ? "ERR loadstate\n" : "OK\n");
        else if (!strcmp(cmd, "reset")) { core->reset(core); keys_held = 0; total_frames = 0; printf("OK\n"); }
        else if (!strcmp(cmd, "rtc") && a1) { setRtc(atoll(a1)); printf("OK\n"); }
        else if (!strcmp(cmd, "framecount")) printf("OK %llu\n", (unsigned long long) total_frames);
        else if (!strcmp(cmd, "regs")) { struct ARMCore *c = core->cpu; printf("OK pc=%08x cpsr=%08x halted=%d r0=%08x r1=%08x lr=%08x sp=%08x\n", (uint32_t) c->gprs[15], c->cpsr.packed, c->halted, c->gprs[0], c->gprs[1], c->gprs[14], c->gprs[13]); }
        else if (!strcmp(cmd, "runto") && a1) {
            /* step until the CPU is about to execute ADDR (thumb), at most N frames; reports registers */
            uint32_t target = strtoul(a1, 0, 0) & ~1u; uint64_t maxf = a2 ? strtoull(a2, 0, 0) : 60;
            struct ARMCore *c = core->cpu; uint64_t f0 = total_frames; int hit = 0; core->setKeys(core, keys_held);
            while (total_frames - f0 < maxf && !hit) {
                for (int i = 0; i < 4000 && !hit; i++) {
                    core->step(core);
                    if ((uint32_t) c->gprs[15] == target + 4 && c->cpsr.t) hit = 1;
                }
                if (!hit) { core->runFrame(core); total_frames++; }
            }
            printf("OK %s pc=%08x lr=%08x r0=%08x r1=%08x sp=%08x\n", hit ? "HIT" : "MISS", (uint32_t) c->gprs[15], c->gprs[14], c->gprs[0], c->gprs[1], c->gprs[13]);
        }
        else if (!strcmp(cmd, "trace") && a1) {
            /* per-instruction run for N frames with a ring buffer of the last 4096 pcs/sps; stops at a wild pc or the reset vector.
               prints the trail (oldest first) to the file in a2 (or stdout summary) */
            uint64_t maxf = strtoull(a1, 0, 0); struct ARMCore *c = core->cpu; static uint32_t rp[4096], rs[4096], rl[4096];
            unsigned idx = 0; unsigned long n = 0; uint32_t startFc = core->frameCounter(core); int stop = 0; core->setKeys(core, keys_held);
            while (core->frameCounter(core) - startFc < maxf && !stop) {
                core->step(core); n++;
                uint32_t pc = (uint32_t) c->gprs[15] - (c->cpsr.t ? 4 : 8);
                rp[idx & 4095] = pc; rs[idx & 4095] = c->gprs[13]; rl[idx & 4095] = c->gprs[14]; idx++;
                int ok = (pc >= 0x08000100 && pc < 0x0A000000) || (pc >= 0x01fffff0 && pc < 0x02040010) || (pc >= 0x02fffff0 && pc < 0x03008010) || pc < 0x4000;
                if (!ok || (pc >= 0x08000000 && pc < 0x08000100)) stop = 1;
            }
            total_frames += core->frameCounter(core) - startFc;
            FILE *f = a2 ? fopen(a2, "w") : NULL;
            unsigned cnt = idx < 4096 ? idx : 4096;
            if (f) { for (unsigned i = 0; i < cnt; i++) { unsigned k = (idx - cnt + i) & 4095; fprintf(f, "%08x sp=%08x lr=%08x\n", rp[k], rs[k], rl[k]); } fclose(f); }
            printf("OK %s steps=%lu pc=%08x sp=%08x lr=%08x\n", stop ? "STOP" : "DONE", n, (uint32_t) c->gprs[15], c->gprs[13], c->gprs[14]);
        }
        else if (!strcmp(cmd, "watchw") && a1 && a2) {
            /* per-instruction watch of one 32-bit word for N frames: prints each change (pc of the writer, lr, sp) up to 40 */
            uint32_t wa = strtoul(a1, 0, 0); uint64_t maxf = strtoull(a2, 0, 0); struct ARMCore *c = core->cpu; int nn = 0; static char wb[8192]; wb[0] = 0;
            uint32_t startFc = core->frameCounter(core); uint32_t old = core->busRead32(core, wa); core->setKeys(core, keys_held);
            while (core->frameCounter(core) - startFc < maxf && nn < 40) {
                core->step(core);
                uint32_t v = core->busRead32(core, wa);
                if (v != old) { printf("CHG %08x -> %08x pc=%08x lr=%08x sp=%08x fr=%u\n", old, v, (uint32_t) c->gprs[15], c->gprs[14], c->gprs[13], core->frameCounter(core) - startFc); old = v; nn++; }
            }
            total_frames += core->frameCounter(core) - startFc;
            printf("OK done %d\n", nn);
        }
        else if (!strcmp(cmd, "safepoint") && a1) { safePoint = strtoul(a1, 0, 0) & ~1u; printf("OK\n"); }
        else if (!strcmp(cmd, "call") && a1) {
            uint32_t ret = 0;
            int rc = callFn(strtoul(a1, 0, 0), a2 ? strtoul(a2, 0, 0) : 0, a3 ? strtoul(a3, 0, 0) : 0,
                            a4 ? strtoul(a4, 0, 0) : 0, a5 ? strtoul(a5, 0, 0) : 0, &ret);
            if (rc) printf("ERR call %d\n", rc); else printf("OK %u\n", ret);
        }
        else printf("ERR unknown\n");
        fflush(stdout);
    }
    return 0;
}

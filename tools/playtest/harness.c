/* Headless mGBA harness for the Orleans playtest bot.
 * Line protocol on stdin; one reply line per command on stdout ("OK ..." or "ERR ...").
 * Build: tools/playtest/build_harness.sh       Run: harness ROM.gba [unix_time [save.sav]]
 * (unix_time is the emulated hardware RTC; the Orleans ROM runs on its own in-game clock (fake RTC), so it ignores it.
 *  save.sav, if given, is loaded as the cartridge's flash save, so a save made by another build can be continued.)
 * Commands:
 *   frames N | press KEYS HOLD [RELEASE] | hold KEYS | release
 *   read8|read16|read32 ADDR | readblock ADDR LEN | write8|write16|write32 ADDR VAL
 *   shot PATH.ppm | hash | nonblack (count of non-black pixels) | savestate PATH | loadstate PATH | reset | rtc UNIXSECS
 *   dumpsave PATH   (writes the cartridge flash save, 128 KiB, to a file: what a real console keeps in battery RAM)
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
static char *savePath;
static struct VFile *savVf;

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
    struct VFile *sav = NULL;
    if (savePath) {
        FILE *f = fopen(savePath, "rb");
        if (!f) return -3;
        fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
        void *buf = malloc(n);
        if (fread(buf, 1, n, f) != (size_t) n) { fclose(f); free(buf); return -3; }
        fclose(f);
        sav = VFileMemChunk(buf, n);
        free(buf);
    } else {
        sav = VFileMemChunk(NULL, 0);
    }
    savVf = sav;
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
static int callMany(int n, uint32_t (*args)[5], uint32_t *rets) {
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
    int rc = 0;
    for (int k = 0; k < n; k++) {
        uint32_t addr = args[k][0], v;
        cpu->halted = 0;
        v = args[k][1]; core->writeRegister(core, "r0", &v);
        v = args[k][2]; core->writeRegister(core, "r1", &v);
        v = args[k][3]; core->writeRegister(core, "r2", &v);
        v = args[k][4]; core->writeRegister(core, "r3", &v);
        v = TRAP | 1; core->writeRegister(core, "lr", &v);
        union PSR p = savedPsr;
        p.t = (addr & 1) ? 1 : 0;
        uint32_t pk = p.packed; core->writeRegister(core, "cpsr", &pk);
        v = addr & ~1u; core->writeRegister(core, "pc", &v);
        long steps = 0; int done = 0;
        while (steps++ < 20000000L) {
            core->step(core);
            uint32_t pc = (uint32_t) cpu->gprs[15];
            if (pc >= TRAP && pc < TRAP + 16) { done = 1; break; }
        }
        if (done && rets) rets[k] = (uint32_t) cpu->gprs[0];
        if (!done) { rc = -2; break; }
    }
    /* restore */
    uint32_t pk = savedPsr.packed; core->writeRegister(core, "cpsr", &pk);
    for (int i = 0; i < 15; i++) { uint32_t r = saved[i]; char nm[8]; snprintf(nm, 8, "r%d", i); core->writeRegister(core, nm, &r); }
    uint32_t pc = (uint32_t) saved[15];
    /* gprs[15] runs ahead of the next instruction by one fetch (+2 thumb / +4 arm); writeRegister wants the address
     * of the next instruction to execute */
    pc -= savedPsr.t ? 2 : 4;
    core->writeRegister(core, "pc", &pc);
    cpu->halted = savedHalt;
    return rc;
}

static int callFn(uint32_t addr, uint32_t a0, uint32_t a1, uint32_t a2, uint32_t a3, uint32_t *ret) {
    uint32_t args[1][5] = {{addr, a0, a1, a2, a3}};
    return callMany(1, args, ret);
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: harness ROM [unix_time]\n"); return 2; }
    romPath = argv[1];
    if (argc > 3) savePath = argv[3];
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
        else if (!strcmp(cmd, "dumpsave") && a1) {
            ssize_t n = savVf->size(savVf);
            uint8_t *buf = malloc(n);
            savVf->seek(savVf, 0, SEEK_SET);
            ssize_t got = savVf->read(savVf, buf, n);
            FILE *f = fopen(a1, "wb");
            if (!f || got != n) printf("ERR dumpsave\n");
            else { fwrite(buf, 1, n, f); printf("OK %zd\n", n); }
            if (f) fclose(f);
            free(buf);
        }
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
        else if (!strcmp(cmd, "stepto") && a1) {
            /* step instruction by instruction until ADDR (thumb entry) is about to run, at most N frames; prints lr, sp and 48 stack words */
            uint32_t target = strtoul(a1, 0, 0) & ~1u; uint64_t maxf = a2 ? strtoull(a2, 0, 0) : 60; struct ARMCore *c = core->cpu;
            uint32_t startFc = core->frameCounter(core); int hit = 0; core->setKeys(core, keys_held);
            static uint32_t ring[8192]; unsigned ri = 0; while (core->frameCounter(core) - startFc < maxf && !hit) { core->step(core); ring[ri++ & 8191] = (uint32_t) c->gprs[15] - 4; if ((uint32_t) c->gprs[15] == target + 4 && c->cpsr.t) hit = 1; } if (hit) { printf("RING"); for (unsigned i = 0; i < 8192; i++) printf(" %08x", ring[(ri + i) & 8191]); printf("%c", 10); }
            total_frames += core->frameCounter(core) - startFc;
            printf("OK %s lr=%08x sp=%08x r0=%08x r1=%08x r2=%08x r3=%08x stack", hit ? "HIT" : "MISS", c->gprs[14], c->gprs[13], c->gprs[0], c->gprs[1], c->gprs[2], c->gprs[3]);
            for (int i = 0; i < 48; i++) printf(" %08x", core->busRead32(core, c->gprs[13] + 4 * i));
            printf("\n");
        }
        else if (!strcmp(cmd, "watchring") && a1 && a2) {
            /* step until the 32-bit word at ADDR changes (at most N frames); prints the last 8192 executed pcs (RING ...) then OK CHG old new sp */
            uint32_t wa = strtoul(a1, 0, 0); uint64_t maxf = strtoull(a2, 0, 0); struct ARMCore *c = core->cpu; static uint32_t ring[8192]; unsigned ri = 0; int hit = 0;
            uint32_t startFc = core->frameCounter(core); uint32_t old = core->busRead32(core, wa); core->setKeys(core, keys_held);
            while (core->frameCounter(core) - startFc < maxf && !hit) { core->step(core); ring[ri++ & 8191] = (uint32_t) c->gprs[15]; if (core->busRead32(core, wa) != old) hit = 1; }
            total_frames += core->frameCounter(core) - startFc;
            printf("RING"); for (unsigned i = 0; i < 8192; i++) printf(" %08x", ring[(ri + i) & 8191]); printf("%c", 10);
            printf("OK %s old=%08x new=%08x sp=%08x r0=%08x r1=%08x r2=%08x r3=%08x lr=%08x%c", hit ? "CHG" : "NONE", old, core->busRead32(core, wa), c->gprs[13], c->gprs[0], c->gprs[1], c->gprs[2], c->gprs[3], c->gprs[14], 10);
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
        else if (!strcmp(cmd, "mapinfo") && a1 && a2 && a3 && a4 && a5) {
            /* mapinfo X0 Y0 W H BEH COLL ELEV SURF : per cell "bb cc ee ss" hex, via the game's own MapGrid functions */
            char *tok[16]; int nt = 0; tok[nt++] = a1; tok[nt++] = a2; tok[nt++] = a3; tok[nt++] = a4; tok[nt++] = a5;
            char *t2; while (nt < 7 && (t2 = strtok(NULL, " \t\r\n"))) tok[nt++] = t2;
            if (nt < 7) { printf("ERR args\n"); fflush(stdout); continue; }
            int x0 = atoi(tok[0]), y0 = atoi(tok[1]), w = atoi(tok[2]), h = atoi(tok[3]);
            uint32_t fb = strtoul(tok[4], 0, 0), fc = strtoul(tok[5], 0, 0), fe = strtoul(tok[6], 0, 0);
            int n = w * h * 4;
            uint32_t (*args)[5] = malloc(sizeof(uint32_t[5]) * (size_t) n * 2);
            uint32_t *rets = calloc((size_t) n * 2, 4);
            int m = 0;
            for (int y = 0; y < h; y++) for (int x = 0; x < w; x++) {
                uint32_t gx = (uint32_t) (x0 + x + 7), gy = (uint32_t) (y0 + y + 7);
                args[m][0] = fb; args[m][1] = gx; args[m][2] = gy; args[m][3] = 0; args[m][4] = 0; m++;
                args[m][0] = fc; args[m][1] = gx; args[m][2] = gy; args[m][3] = 0; args[m][4] = 0; m++;
                args[m][0] = fe; args[m][1] = gx; args[m][2] = gy; args[m][3] = 0; args[m][4] = 0; m++;
            }
            int rc = callMany(m, args, rets);
            if (rc) printf("ERR mapinfo %d\n", rc);
            else {
                printf("OK ");
                for (int i = 0; i < w * h; i++) {
                    printf("%02x%02x%02x ", rets[i * 3] & 0xFF, rets[i * 3 + 1] & 0xFF, rets[i * 3 + 2] & 0xFF);
                }
                printf("\n");
            }
            free(args); free(rets);
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

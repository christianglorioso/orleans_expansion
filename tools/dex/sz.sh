# prints sizeof(SaveBlock1)/SaveBlock2 compiled with the real ROM flags (limit for SaveBlock1: 15872)
cd ~/orleans_dex_pp
rsync -a /mnt/c/Users/chris/orleans_expansion/orleans_expansion/include/ include/
cat > t.c <<'EOF'
#include "global.h"
char (*x)[sizeof(struct SaveBlock1)] = 1;
char (*y)[sizeof(struct SaveBlock2)] = 1;
EOF
arm-none-eabi-gcc -c -iquote include -Wno-trigraphs -DMODERN=1 -DTESTING=0 -DEMERALD -std=gnu17 -mthumb -mthumb-interwork -O2 -mabi=apcs-gnu -mtune=arm7tdmi -march=armv4t t.c -o /dev/null 2>&1 | grep -o "char (\*)\[[0-9]*\]" | sort -u

cd ~/orleans_dex_pp
rsync -a /mnt/c/Users/chris/orleans_expansion/orleans_expansion/include/ include/
rsync -a /mnt/c/Users/chris/orleans_expansion/orleans_expansion/src/save.c src/save.c
arm-none-eabi-gcc -fsyntax-only -iquote include -Wno-trigraphs -DMODERN=1 -DTESTING=0 -DEMERALD -std=gnu17 src/save.c 2>&1 | head -8
cat > t.c <<'EOF'
#include "global.h"
char (*x)[sizeof(struct SaveBlock1)] = 1;
EOF
arm-none-eabi-gcc -c -iquote include -Wno-trigraphs -DMODERN=1 -DTESTING=0 -DEMERALD -std=gnu17 t.c -o /dev/null 2>&1 | grep -o "char (\*)\[[0-9]*\]" | sort -u

#include <mach-o/dyld.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

int main(void) {
    char path[PATH_MAX];
    uint32_t n = sizeof(path);

    _NSGetExecutablePath(path, &n);

    // .../MyTool.app/Contents/MacOS/launcher
    *strrchr(path, '/') = 0;  // MacOS
    *strrchr(path, '/') = 0;  // Contents

    char script[PATH_MAX];
    snprintf(script, sizeof(script),
             "%s/Resources/src/main.py", path);

    execl("/usr/bin/python3", "python3", script, NULL);

    return 1;
}
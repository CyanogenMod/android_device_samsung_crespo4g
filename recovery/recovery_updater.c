/*
 * Copyright (C) 2011 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <ctype.h>
#include <errno.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <fcntl.h>

#include "cutils/misc.h"
#include "cutils/properties.h"
#include "edify/expr.h"
#include "mincrypt/sha.h"
#include "minzip/DirUtil.h"
#include "mtdutils/mounts.h"
#include "mtdutils/mtdutils.h"


/* ioctl commands for /dev/dpram_recovery */
#define IOCTL_MODEM_FW_UPDATE	_IO('D',0x1)
#define IOCTL_MODEM_CHK_STAT	_IO('D',0x2)
#define IOCTL_MODEM_PWROFF	_IO('D',0x3)

/* modem status during update */
struct stat_info {
	int pct;
	char msg[0x100];
};

/* buffer type for modem delta */
struct dpram_firmware {
	char *firmware;
	int size;
	int is_delta;
};

Value* UpdateModemFn(const char* name, State* state,
                     int argc, Expr* argv[]) {

    struct dpram_firmware fw;
    struct stat_info st;
    int ofd = -1;
    int err = -1;
    int prev_pct = -1;

    if (argc != 1)
        return ErrorAbort(state, "%s() expects 1 arg, got %d", name, argc);

    Value* radio;
    if (ReadValueArgs(state, argv, 1, &radio) != 0) {
        return NULL;
    }
    if (radio->type != VAL_BLOB) {
        ErrorAbort(state, "argument to %s() has wrong type", name);
        FreeValue(radio);
        return NULL;
    }

    if (radio->size <= 0) {
        fprintf(stderr, "%s(): no file contents received", name);
        return StringValue(strdup(""));
    }

    printf("UpdateModemFn with %d bytes\n", radio->size);

    /* open modem device */
    ofd = open("/dev/modem_ctl", O_RDWR);

    if (ofd < 0) {
        printf("Unable to open modem device (%s)\n", strerror(errno));
        goto out;
    }

    /* initiate firmware update */
    fw.firmware = radio->data;
    fw.size = radio->size;
    fw.is_delta = 0;
    err = ioctl(ofd, IOCTL_MODEM_FW_UPDATE, &fw);

    if (err < 0) {
        printf("ioctl failed with %d\n", err);
        goto out;
    }

    do {
        err = ioctl(ofd, IOCTL_MODEM_CHK_STAT, &st);
        if (prev_pct != st.pct) {
            /* use st.pct to update UI */
            printf(" %3d \%\n", st.pct);
            prev_pct = st.pct;
        }

        if (err < 0) {
            /* Aborted if an error occurrs during update */
            printf("Update error %d\n", err);
            printf("Error msg : %s\n", st.msg);

            ioctl(ofd, IOCTL_MODEM_PWROFF, NULL);
            goto out;
        }
    } while (err);

    printf("Firmware Update is Successful!\n");

out:
    FreeValue(radio);
    if (ofd >= 0)
        close(ofd);

    return StringValue(strdup(err == 0 ? "t" : ""));
}

void Register_librecovery_updater_crespo4g() {
    printf("Register_librecovery_updater_crespo4g is called\n");
    RegisterFunction("samsung.update_modem", UpdateModemFn);
}

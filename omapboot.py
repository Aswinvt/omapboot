#!/usr/bin/env python3
"""
omap44xx USB pre-bootloader loader.

usage: omapboot [-a] aboot.bin uboot.bin
 -a means "don't wait for user input to upload u-boot"

See README.md for detailed usage.

Credits:
* Brian Swetland, for the original version <https://github.com/swetland/omap4boot>
* Dmitry Pervushin, for clues <https://github.com/dmitry-pervushin/usbboot-omap4>
* Won Kyu Park, the Windows version and the clues that finally put this together.
* Nick Guenther, for python port.
* Texas Instruments, for publishing their canon, even though omapflash is spaghetticode from hell <https://gforge.ti.com/gf/project/flash/>
"""

import sys
import time

try:
    from usbbulk import BulkUSB
except ImportError:
    raise SystemExit("No USB API available.")

from OMAP import *

if __name__ == '__main__':
    print("Waiting for omap44 device. Make sure you start with the battery out.")
    
    # USB IDs:
    VENDOR = 0x0451
    PRODUCT = 0xd00f #TODO: this needs to be a list; XXX pyusb has hooks that make it easy to implement this... but openbsd doesn't
    
    # As far as I can tell, without kernel hooks (which are too
    # platform-specific for this code) USB has no way to register
    # event handlers. So I'm stuck with polling:
    while True:
        try:
            port = BulkUSB(VENDOR, PRODUCT)
            break
        except OSError:
            pass
        time.sleep(0.1)
        
    
    omap = OMAP4(port)
    
    # Read the chip ident. This isn't necessary for booting,
    # but it's useful for debugging different peoples' results.
    ASIC_ID = omap.id()
    print("ASIC_ID:")
    print(" ".join(hex(e) for e in ASIC_ID))
    #assert ASIC_ID["ID"][0] == 0x44, "This code expects an OMAP44xx device"
    
    # quick hack implementation of a command line arg
    # TODO: use the proper command parser, or at least getopt
    # 
    #this means "don't block at input() to let the user insert the battery"
    # if you are doing rapid dev cycles, having to press two enters for each upload would get tedious
    AUTOFLAG = False
    if sys.argv[1] == "-a":
        AUTOFLAG = True 
        del sys.argv[1]
    
    assert len(sys.argv) == 3, "usage: usbboot [-a] 2ndstage.bin 3rdstage.bin"
    
    omap.boot(sys.argv[1], sys.argv[2], AUTOFLAG)
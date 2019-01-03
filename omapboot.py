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

if("win" in sys.platform):
    print("We are not support Windows Platform!")
    raise SystemExit(1)

try:
    from usbbulk import BulkUSB
except ImportError:
    raise SystemExit("No USB API available.")

from OMAP import *

def main():
    AUTOFLAG = False
    CHANGEBOOT = False
    if len(sys.argv) < 2:
        print("usage for load boot loader: usbboot [-a] 2ndstage.bin 3rdstage.bin")
        print("usage for change boot device: usbboot -b")
        raise SystemExit(1)
    if sys.argv[1] == "-b":
        print("Boot from MMC1 interface selected.")
        print("Waiting for omap44 device.")
        CHANGEBOOT = True
    elif len(sys.argv) in [3,4]:
    #this means "don't block at input() to let the user insert the battery"
    # if you are doing rapid dev cycles, having to press two enters for each upload would get tedious
        if sys.argv[1] == "-a":
            AUTOFLAG = True 
            del sys.argv[1]
        aboot, uboot = sys.argv[1:]
        print("Waiting for omap44 device. Make sure you start with the battery out.")
    else:
        print("usage: usbboot [-a] 2ndstage.bin 3rdstage.bin")
        raise SystemExit(1)
    
    # quick hack implementation of a command line arg
    # TODO: use the proper command parser, or at least getopt
    # 

    
    
    # USB IDs:
    #TODO: these need to be a list;
    # pyusb has hooks that make it easy to implement this...
    # but I'll have to write my own for ugen(4) doesn't
    VENDOR = 0x0451
    PRODUCT = 0xd00f 
    # from TI's <https://gforge.ti.com/gf/project/flash>/trunk/omapflash/host/fastboot.c
    # interestingly, they don't bother to use product IDs
    #VENDOR = [0x18d1, 0x0451, 0x0bb4]
    #CLASS = [0xFF]
    #SUBCLASS = [0x42]
    #PROTOCOL = [0x03]
    
    
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
    #print("ASIC_ID:")
    #print(" ".join(hex(e) for e in ASIC_ID))
    #assert ASIC_ID["ID"][0] == 0x44, "This code expects an OMAP44xx device"
    if CHANGEBOOT:
        omap.bootMMC1()
    else:
        omap.boot(aboot, uboot, AUTOFLAG)
    
if __name__ == '__main__':
    main()
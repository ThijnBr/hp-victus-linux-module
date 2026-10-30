# normal makefile
KERNELDIR ?= /lib/modules/`uname -r`/build

ifeq ($(shell grep -s '^CONFIG_CC_IS_CLANG=y' $(KERNELDIR)/.config),CONFIG_CC_IS_CLANG=y)
  CC ?= clang
  LLVM ?= 1
  export CC LLVM
endif

default:
	$(MAKE) -C $(KERNELDIR) M=$$PWD

# Module specific targets
genbin:
	echo "X" > hp-wmi_bin.o_shipped

clean:
	-$(RM) -f *.a *.ko *.o *.mod *.mod.c *.order *.symvers

.PHONY: clean


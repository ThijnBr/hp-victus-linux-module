.PHONY: all build install uninstall clean load unload

all: build

build:
	$(MAKE) -C src

clean:
	$(MAKE) -C src clean

install:
	sudo dkms install .

uninstall:
	sudo dkms remove hp-victus-wmi/1.0.0 --all

load:
	sudo modprobe hp_wmi

unload:
	sudo modprobe -r hp_wmi

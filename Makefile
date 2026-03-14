install:
	sudo dkms install .

uninstall:
	sudo dkms remove hp-omen-wmi/0.6.2 --all

all: install

savedcmd_hp-wmi.mod := printf '%s\n'   hp-wmi.o | awk '!x[$$0]++ { print("./"$$0) }' > hp-wmi.mod

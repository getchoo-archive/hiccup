# hiccup

hiccup is a python script that attempts to upgrade your system with multiple package managers.

## how it works
hiccup reads from `$XDG_CONFIG_HOME/hiccup/config.json`. this file specifies distros (by their freedesktop id), shell plugin
managers, and other package managers, paired with a command that runs an update - see `default-config.json`.

## how to install
hiccup only needs one command to install :)
```sh
make install
```

and to uninstall:
```sh
make uninstall
```

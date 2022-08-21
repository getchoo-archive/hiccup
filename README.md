# hiccup

hiccup is a python script that attempts to upgrade your system with multiple package managers.

## how it works
hiccup reads from `$XDG_CONFIG_HOME/hiccup/config.json`. this file must contain 5 objects:

- `system_update_cmds`
- `extra_cmds`
- `clean_cmds`
- `shell_plugin_cmds`
- `other_cmds`

the value for most keys will be run with `bash -c`, but values in `system_update_cmds` and `clean_cmds`
will run with `sudo bash -c` and values in `shell_plugin_cmds` will run with name of the shell specified.

see `default-config.json` for example

## how to install
hiccup only needs one command to install :)
```sh
python setup.py install --user
```

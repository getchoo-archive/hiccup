# fedora packaging

## how to build
```sh
spectool --get-files hiccup.spec
fedpkg --release f36 mockbuild
find -type f -name 'hiccup*noarch.rpm' -exec sudo dnf install {} \;
```

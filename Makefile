shell = /usr/bin/env bash
CONFIG = $(HOME)/.config
ifeq ($(XDG_CONFIG_HOME),)
	CONFIG = $(XDG_CONFIG_HOME)
endif

install:
	install -Dm755 bin/hiccup $(DESTDIR)$(PREFIX)/bin/hiccup
	install -Dm644 default-config.json $(DESTDIR)$(CONFIG)/hiccup/config.json

uninstall:
	rm $(DESTDIR)$(PREFIX)/bin/hiccup
	rm $(DESTDIR)$(CONFIG)/hiccup/config.json

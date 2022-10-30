SHELL=/bin/sh

.SILENT:
.IGNORE:

install: text_to_tex.py
	cp ./text_to_tex.py ~/.local/bin/
	chmod 744 ~/.local/bin/text_to_tex.py

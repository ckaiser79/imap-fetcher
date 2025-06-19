# Name des Archivs
ARCHIV=target/imap-fetcher.tgz

# Dateien und Verzeichnisse, die ins Archiv sollen
INCLUDE=README.md main.py lib vendor

.PHONY: all clean pack

all: pack

pack:
	mkdir -p target/src/vendor
	cp -r README.md main.py lib target/src/
	rm -rf target/src/lib/__pycache__
	cp vendor/__init__.py target/src/vendor/
	tar -czvf $(ARCHIV) -C target/src/ $(INCLUDE)

clean:
	rm -rf target


PKGDIR := pkgdir
BINFILE := $(PKGDIR)/build/x86_64-unknown-linux-gnu/debug/exe/diskpatrol

diskpatrol:
	python3 -m pip install -U pip
	python3 -m pip install pyoxidizer
	curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | \
		sh -s -- --no-modify-path -y
	@echo $(PKGDIR)
	pyoxidizer build --system-rust --path=$(PKGDIR)
	strip $(BINFILE)
	mv $(BINFILE) .

install: diskpatrol
	install -m 0755 $(BINFILE) /usr/bin


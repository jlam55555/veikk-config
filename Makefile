PIP?=python3 -m pip
PKG_NAME?=veikk-config
PIP_INSTALL_FLAGS+=--prefix=/usr/local --upgrade

SYSTEMD_SERVICE?=veikkd
SYSTEMD_SRC?=systemd/$(SYSTEMD_SERVICE).service
SYSTEMD_TARGET=/usr/lib/systemd/system/

.PHONY: install
install:
	$(PIP) install $(PIP_INSTALL_FLAGS) .
	cp $(SYSTEMD_SRC) $(SYSTEMD_TARGET)

.PHONY: uninstall
uninstall:
	$(PIP) uninstall $(PKG_NAME)
	rm $(SYSTEMD_TARGET)/$(SYSTEMD_SERVICE).service
PIP?=python3 -m pip
PKG_NAME?=veikk-config
PIP_INSTALL_FLAGS+=--prefix=/usr/local --upgrade

CONF_BASE?=conf_files

SYSTEMD_SERVICE?=veikkd
SYSTEMD_SRC?=$(CONF_BASE)/$(SYSTEMD_SERVICE).service
SYSTEMD_TARGET=/usr/lib/systemd/system/

# install: install pip package and configuration files
.PHONY: install
install: install_files
	$(PIP) install $(PIP_INSTALL_FLAGS) .

# install_files: install configuration files only
.PHONY: install_files
install_files:
	cp $(SYSTEMD_SRC) $(SYSTEMD_TARGET)

# uninstall: uninstall pip package and configuration files
.PHONY: uninstall
uninstall: uninstall_files
	$(PIP) uninstall $(PKG_NAME)

# uninstall_files: uninstall configuration files only
.PHONY: uninstall_files
uninstall_files:
	rm $(SYSTEMD_TARGET)/$(SYSTEMD_SERVICE).service
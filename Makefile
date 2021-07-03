PIP             ?=python3 -m pip
PKG_NAME        ?=veikk-config
PIP_INSTALL_FLAGS+=--prefix=/usr/local --upgrade

CONF_BASEDIR    ?=conf_files

SYSTEMD_SERVICE ?=veikkd
SYSTEMD_SRC     ?=$(SYSTEMD_SERVICE).service
SYSTEMD_TARGET  ?=/usr/lib/systemd/system

DBUS_BUS_NAME	?=com.veikk.veikkd
DBUS_SRC        ?=$(DBUS_BUS_NAME).conf
DBUS_TARGET     ?=/usr/share/dbus-1/system.d

# install: install pip package and configuration files
.PHONY: install
install: install_files
	$(PIP) install $(PIP_INSTALL_FLAGS) .

# install_files: install configuration files only
.PHONY: install_files
install_files:
	install $(CONF_BASEDIR)/$(SYSTEMD_SRC) $(SYSTEMD_TARGET)
	install $(CONF_BASEDIR)/$(DBUS_SRC) $(DBUS_TARGET)

# uninstall: uninstall pip package and configuration files
.PHONY: uninstall
uninstall: uninstall_files
	-$(PIP) uninstall $(PKG_NAME)

# uninstall_files: uninstall configuration files only
.PHONY: uninstall_files
uninstall_files:
	-rm $(SYSTEMD_TARGET)/$(SYSTEMD_SRC)
	-rm $(DBUS_TARGET)/$(DBUS_SRC)
# INSTALL.md

---

TODO: pip package ...??? can't really do full install on its own
TODO: package for different distros

---

## Prerequisites
`veikk-config` depends on Python >=3.7 and the following packages: `evdev`, `pyudev`, `yaml` (PyYAML), `dbus`, `xlib`, and (optionally) `wxPython`.

The following instructions are shown for Debian 10. Use the appropriate package manager for your Linux distribution.

### Using package manager (recommended)
This is the easiest and fastest way to install the packages.
```
$ apt install python3-evdev python3-pyudev python3-yaml python3-dbus python3-xlib
```
Optionally (for screen mapping selector GUI):
```
$ apt install python3-wxgtk4.0
```

---
### Within a virtual environment (advanced)
Building within a venv is useful for development, but is slower because it requires building the wheels.
```
$ apt install python3-pip python3-venv
$ python3 -m venv venv
$ . venv/bin/activate
(venv) $ pip install -r requirements.txt
```
You may need to install additional packages as prerequisites to `pip install`. For example, on a fresh Debian 10 system the following packages were also necessary for the `pip install`:
```
(venv) $ apt install pkg-config libdbus-1-dev libglib2.0-dev
```
Pay close attention to the error messages.

#### Installing wxPython (for screen mapping selector GUI):
wxPython is an optional dependency because the screen mapping can be done from the CLI without a GUI, and because it is somewhat heavy.

Building the wheel via pip (very slow):
```
(venv) $ pip install -r optional_requirements.txt
```
[Downloading a wheel][wxpython-whl] (faster):
```
(venv) $ pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/debian-10 wxPython
```
Also pay close attention to the error messages: on Debian 10, `libSDL2-2.0` also had to be installed:
```
$ apt install libSDL2-2.0
```

---

## Installing the `veikk-config` package
```
$ sudo make install
```

### Uninstallation
```
$ sudo make uninstall
```

[wxpython-whl]: https://wxpython.org/pages/downloads/index.html

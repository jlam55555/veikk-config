# VEIKK Linux Driver V3 Configuration tool
The configuration tool for the VEIKK driver (v3).

For the old version of the VEIKK driver (v2), see [this configuration tool][v2-gui]. These are not compatible.

---

### Description

TODO lorem ipsum

This includes two command-line scripts:
- `veikk`: a daemon that services requests and performs the button mappings -- must be run as root
- `veikkctl`: a CLI to configure the veikk daemon

---

### Install
Install the package globally, so that the root user can access the scripts (necessary for running the daemon).

Type hints are used, so this requires at least Python 3.5.

TODO: notes about prerequisites...

```bash
$ sudo python3 -m pip install --prefix=/usr/local veikkd-config
```
(If you have a venv set up, make sure it is not active -- you want to be using the global Python environment.)

##### Uninstall
```bash
$ sudo python3 -m pip uninstall veikkd-config
```

---

### Build
Prerequisites: Python 3 (tested on 3.8.2), pip 3

##### Initial setup
It's recommended to build this in a venv.

Create, activate, and set up the venv.
```bash
$ python3 -m venv venv
$ . venv/bin/activate
(venv) $ pip install -r requirements.txt
```
You only have to create the venv and install the requirements once (unless the dependencies change). To deactivate the venv:
```bash
(venv) $ deactivate
$ # out of the venv now
```

##### Testing
To test the programs without `pip install`-ing them every time, you can use the helper scripts:
```bash
(venv) $ python 
```

##### Install the package (locally)
The `veikk` and `veikkctl` packages will be installed using distutils. These will expose the [command line scripts](https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html) of the same name.
```bash
(venv) $ pip install .
(venv) $ veikkd         # run veikkd config daemon
(venv) $ veikkctl       # run veikk config interface
```

[v2-gui]: https://www.github.com/jlam55555/veikk-linux-driver-gui
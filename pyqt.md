# PyQt5 Installation on Jetson Nano

This guide helps you install **PyQt5 from source** on a Jetson Nano.

---

## Requirements

```bash
sudo apt update && sudo apt upgrade
sudo apt install -y build-essential python3-dev python3-pip \
    qt5-qmake qtbase5-dev qttools5-dev qttools5-dev-tools \
    libgl1-mesa-dev libxkbcommon-x11-0
```

---

##  Install SIP

### Option A: SIP 4.x (for PyQt5 ≤ 5.15.0)

```bash
wget https://www.riverbankcomputing.com/static/Downloads/sip/4.19.25/sip-4.19.25.tar.gz
tar -xvzf sip-4.19.25.tar.gz
cd sip-4.19.25
python3 configure.py
make -j$(nproc)
sudo make install
```

### Option B: SIP 5.x

```bash
pip3 install sip
```

---

##  Install PyQt5

```bash
wget https://files.pythonhosted.org/packages/source/P/PyQt5/PyQt5_gpl-5.15.0.tar.gz
tar -xvzf PyQt5_gpl-5.15.0.tar.gz
cd PyQt5_gpl-5.15.0
python3 configure.py --qmake /usr/lib/aarch64-linux-gnu/qt5/bin/qmake
make -j$(nproc)
sudo make install
```

---

##  Test PyQt5

```python
# test_pyqt5.py
import sys
from PyQt5.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)
label = QLabel("Hello, PyQt5!")
label.show()
sys.exit(app.exec_())
```

Run it:

```bash
python3 test_pyqt5.py
```

---

##  Optional (Skip Compilation)

```bash
sudo apt install python3-pyqt5
```

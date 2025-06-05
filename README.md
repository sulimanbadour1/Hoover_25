# Sensor Control Application - Ubuntu Installation Guide (Jetson Edition)

## Overview
This application provides a control interface for various sensors including Intel RealSense cameras (L515, D435), RP Lidar, and TI Radar. It offers real-time data visualization, device control, and data acquisition capabilities. This guide is specifically optimized for NVIDIA Jetson devices running Ubuntu.

## System Requirements
- NVIDIA Jetson device (Nano, Xavier NX, or AGX Xavier)
- JetPack 4.6 or newer
- Ubuntu 20.04 LTS (comes with JetPack)
- Python 3.8 (comes with JetPack)
- USB 3.0 ports (required for Intel RealSense devices)
- Minimum 4GB RAM
- 10GB free disk space
- CUDA support (comes with JetPack)

## Pre-Installation Checks
```bash
# Check JetPack version
sudo apt-cache show nvidia-l4t-core
# or
cat /etc/nv_tegra_release

# Check Python version
python3 --version

# Check CUDA version
nvcc --version

# Check available disk space
df -h

# Check USB 3.0 ports
lsusb -t | grep "SuperSpeed"
```

## Installation Steps

### 1. System Updates and Dependencies
```bash
# Update system packages
sudo apt update
sudo apt upgrade

# Install required system packages
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    libusb-1.0-0-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-dev \
    git \
    cmake \
    build-essential \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libglfw3-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libopencv-dev \
    libomp-dev

# Install CUDA dependencies (if not already installed with JetPack)
sudo apt install -y \
    cuda-toolkit-10-2 \
    libcudnn8 \
    libcudnn8-dev
```

### 2. Create and Activate Virtual Environment
```bash
# Create a new directory for the project
mkdir -p ~/sensor_control_app
cd ~/sensor_control_app

# Create virtual environment with specific Python version
python3.8 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify Python version in virtual environment
python --version  # Should show Python 3.8.x
```

### 3. Install Python Dependencies
```bash
# Upgrade pip and install wheel
pip install --upgrade pip
pip install wheel

# Install required Python packages with specific versions
pip install \
    PyQt5==5.15.9 \
    numpy==1.24.3 \
    opencv-python==4.8.0.74 \
    pyserial==3.5 \
    scipy==1.10.1 \
    matplotlib==3.7.1 \
    cython==0.29.33 \
    setuptools==65.5.1
```

### 4. Intel RealSense SDK Installation for Jetson
```bash
# Install RealSense SDK dependencies
sudo apt-get install -y \
    libusb-1.0-0-dev \
    libglfw3-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    cmake \
    libssl-dev

# Clone RealSense SDK
cd ~
git clone https://github.com/IntelRealSense/librealsense.git
cd librealsense

# Configure and build for Jetson
mkdir build && cd build
cmake .. -DBUILD_EXAMPLES=true -DBUILD_GRAPHICAL_EXAMPLES=false -DBUILD_WITH_CUDA=true -DCMAKE_BUILD_TYPE=release -DFORCE_RSUSB_BACKEND=true -DBUILD_WITH_TM2=false -DHWM_OVER_XU=false

# Build and install
make -j4
sudo make install

# Update library path
sudo ldconfig

# Install pyrealsense2 for Jetson
# First, copy the provided .so file to the correct location
sudo cp /path/to/your/pyrealsense2.cpython-38-aarch64-linux-gnu.so /usr/local/lib/python3.8/dist-packages/

# Set proper permissions
sudo chmod 644 /usr/local/lib/python3.8/dist-packages/pyrealsense2.cpython-38-aarch64-linux-gnu.so

# Install udev rules
sudo wget -O /etc/udev/rules.d/99-realsense-libusb.rules https://raw.githubusercontent.com/IntelRealSense/librealsense/master/config/99-realsense-libusb.rules
sudo udevadm control --reload-rules && sudo udevadm trigger

# Verify installation
python3 -c "import pyrealsense2 as rs; print('RealSense SDK version:', rs.__version__)"
```

### 5. RP Lidar Setup for Jetson
```bash
# Install RP Lidar dependencies
sudo apt-get install -y \
    ros-noetic-rplidar-ros \
    ros-noetic-rplidar \
    ros-noetic-rplidar-ros

# Add user to dialout group for serial port access
sudo usermod -a -G dialout $USER

# Create udev rules for RP Lidar
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="plugdev"' | sudo tee /etc/udev/rules.d/99-rplidar.rules

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 6. TI Radar Setup
```bash
# Create directory for TI Radar
sudo mkdir -p /opt/ti-radar
sudo chown $USER:$USER /opt/ti-radar

# Copy configuration file
cp konfigurace.cfg /opt/ti-radar/

# Create udev rules for TI Radar
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="0451", ATTRS{idProduct}=="bef3", MODE="0666", GROUP="plugdev"' | sudo tee /etc/udev/rules.d/99-ti-radar.rules

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 7. Application Setup
```bash
# Clone or copy the application files
cd ~/sensor_control_app

# Set proper permissions
chmod +x MainWindow.py

# Create a desktop shortcut (optional)
cat > ~/Desktop/SensorControl.desktop << EOL
[Desktop Entry]
Version=1.0
Type=Application
Name=Sensor Control
Comment=Sensor Control Application
Exec=bash -c "cd ~/sensor_control_app && source venv/bin/activate && python3 MainWindow.py"
Icon=utilities-terminal
Terminal=true
Categories=Utility;
EOL

chmod +x ~/Desktop/SensorControl.desktop
```

### 8. Verify All Components
```bash
# Test Intel RealSense
python3 -c "import pyrealsense2 as rs; print('RealSense SDK version:', rs.__version__)"

# Test RP Lidar
python3 -c "import serial.tools.list_ports; print('Available ports:', [port.device for port in serial.tools.list_ports.comports()])"

# Test OpenCV
python3 -c "import cv2; print('OpenCV version:', cv2.__version__)"

# Test PyQt5
python3 -c "from PyQt5.QtCore import QT_VERSION_STR; print('Qt version:', QT_VERSION_STR)"
```

## Running the Application
```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
python3 MainWindow.py
```

## Troubleshooting

### Common Issues and Solutions

1. **Intel RealSense Camera Not Detected**
   ```bash
   # Check if the device is recognized
   lsusb | grep Intel
   
   # Check RealSense SDK installation
   realsense-viewer
   
   # Reinstall RealSense SDK if needed
   cd ~/librealsense
   mkdir build && cd build
   cmake .. -DBUILD_EXAMPLES=true -DBUILD_GRAPHICAL_EXAMPLES=false -DBUILD_WITH_CUDA=true -DCMAKE_BUILD_TYPE=release -DFORCE_RSUSB_BACKEND=true -DBUILD_WITH_TM2=false -DHWM_OVER_XU=false
   make -j4
   sudo make install
   ```

2. **Permission Issues**
   ```bash
   # Add user to all necessary groups
   sudo usermod -a -G video,dialout,plugdev,users $USER
   
   # Check current groups
   groups
   
   # Log out and log back in for changes to take effect
   ```

3. **Python Package Issues**
   ```bash
   # Check Python path
   python3 -c "import sys; print('\n'.join(sys.path))"
   
   # Recreate virtual environment
   deactivate
   rm -rf venv
   python3.8 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt  # If available
   ```

4. **USB Port Issues**
   ```bash
   # Check USB port status
   lsusb -t
   
   # Check USB port permissions
   ls -l /dev/ttyUSB*
   ls -l /dev/ttyACM*
   
   # Check USB power
   sudo cat /sys/bus/usb/devices/*/power/control
   ```

5. **Jetson-Specific Issues**
   ```bash
   # Check GPU memory
   sudo tegrastats
   
   # Check CPU frequency
   cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq
   
   # Check temperature
   cat /sys/class/thermal/thermal_zone*/temp
   ```

## Device-Specific Information

### Intel RealSense Devices
- L515 Serial Number: f1320623
- Front D435 Serial Number: 241122074115
- Back D435 Serial Number: 241222076731
- Supported resolutions and frame rates:
  - D435: Up to 1280x720 @ 90fps
  - L515: Up to 1024x768 @ 30fps

### RP Lidar
- Default baud rate: 115200
- Device appears as: /dev/ttyUSB0 (or similar)
- Supported scan rate: 5.5 Hz
- Range: 0.15m - 12.0m

### TI Radar
- Configuration file: /opt/ti-radar/konfigurace.cfg
- Default settings:
  - Frequency: 77 GHz
  - Range Resolution: 0.044m
  - Maximum Range: 9.02m
  - Frame Duration: 100ms

## Performance Optimization for Jetson

1. **Power Mode Settings**
   ```bash
   # Check current power mode
   sudo nvpmodel -q
   
   # Set to maximum performance mode
   sudo nvpmodel -m 0
   
   # Set to maximum efficiency mode
   sudo nvpmodel -m 1
   ```

2. **Fan Control**
   ```bash
   # Check fan status
   sudo tegrastats
   
   # Manual fan control (if needed)
   sudo sh -c 'echo 255 > /sys/kernel/debug/tegra_fan/target_pwm'
   ```

3. **Memory Management**
   ```bash
   # Check memory usage
   free -h
   
   # Clear system cache
   sudo sync; echo 3 | sudo tee /proc/sys/vm/drop_caches
   ```

## Support
For issues and support:
1. Check the troubleshooting section above
2. Verify all dependencies are correctly installed
3. Ensure proper USB connections and permissions
4. Check system logs:
   ```bash
   # Check system logs
   dmesg | grep -i usb
   journalctl -f
   
   # Check RealSense logs
   realsense-viewer --log-level debug
   ```

# Sensor Control Application - Ubuntu Installation Guide

## Overview
This application provides a control interface for various sensors including Intel RealSense cameras (L515, D435), RP Lidar, and TI Radar. It offers real-time data visualization, device control, and data acquisition capabilities.

## System Requirements
- Ubuntu 20.04 LTS or newer
- Python 3.8 or higher
- USB 3.0 ports (required for Intel RealSense devices)
- Minimum 4GB RAM
- 10GB free disk space

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
    zlib1g-dev
```

### 2. Create and Activate Virtual Environment
```bash
# Create a new directory for the project (if not already created)
mkdir -p ~/sensor_control_app
cd ~/sensor_control_app

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 3. Install Python Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install required Python packages
pip install \
    PyQt5==5.15.9 \
    numpy==1.24.3 \
    opencv-python==4.8.0.74 \
    pyserial==3.5 \
    pyrealsense2==2.53.1.4425 \
    scipy==1.10.1 \
    matplotlib==3.7.1
```

### 4. Intel RealSense SDK Installation
```bash
# Register the server's public key
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE || sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE

# Add the server to the list of repositories
sudo add-apt-repository "deb https://librealsense.intel.com/Debian/apt-repo $(lsb_release -cs) main" -u

# Install the libraries
sudo apt-get update
sudo apt-get install -y librealsense2-dkms librealsense2-utils librealsense2-dev librealsense2-dbg

# Install udev rules
sudo wget -O /etc/udev/rules.d/99-realsense-libusb.rules https://raw.githubusercontent.com/IntelRealSense/librealsense/master/config/99-realsense-libusb.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
```

### 5. RP Lidar Setup
```bash
# Install RP Lidar dependencies
sudo apt-get install -y \
    ros-noetic-rplidar-ros \
    ros-noetic-rplidar \
    ros-noetic-rplidar-ros

# Add user to dialout group for serial port access
sudo usermod -a -G dialout $USER
```

### 6. TI Radar Setup
```bash
# Create directory for TI Radar
sudo mkdir -p /opt/ti-radar
sudo chown $USER:$USER /opt/ti-radar

# Copy configuration file
cp konfigurace.cfg /opt/ti-radar/
```

### 7. Clone and Setup Application
```bash
# Clone the repository (if not already done)
git clone <repository-url> .
# OR copy the files to the current directory if you have them locally

# Set proper permissions
chmod +x MainWindow.py
```

### 8. USB Device Rules
```bash
# Create udev rules for all sensors
sudo nano /etc/udev/rules.d/99-sensors.rules

# Add the following lines:
SUBSYSTEM=="usb", ATTRS{idVendor}=="8086", ATTRS{idProduct}=="0b5c", MODE="0666", GROUP="plugdev"  # Intel RealSense
SUBSYSTEM=="usb", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="plugdev"  # RP Lidar
SUBSYSTEM=="usb", ATTRS{idVendor}=="0451", ATTRS{idProduct}=="bef3", MODE="0666", GROUP="plugdev"  # TI Radar

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 9. Verify Installation
```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate

# Test Intel RealSense
python3 -c "import pyrealsense2 as rs; print('RealSense SDK version:', rs.__version__)"

# Test RP Lidar
python3 -c "import serial.tools.list_ports; print('Available ports:', [port.device for port in serial.tools.list_ports.comports()])"
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
   
   # Reinstall RealSense SDK if needed
   sudo apt-get remove --purge librealsense2*
   sudo apt-get update
   sudo apt-get install librealsense2-dkms librealsense2-utils librealsense2-dev
   ```

2. **Permission Issues**
   ```bash
   # Add user to necessary groups
   sudo usermod -a -G video,dialout,plugdev $USER
   
   # Log out and log back in for changes to take effect
   ```

3. **Python Package Issues**
   ```bash
   # Recreate virtual environment
   deactivate
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt  # If available
   ```

4. **USB Port Issues**
   ```bash
   # Check USB port status
   lsusb
   
   # Check USB port permissions
   ls -l /dev/ttyUSB*
   ls -l /dev/ttyACM*
   ```

## Device-Specific Information

### Intel RealSense Devices
- L515 Serial Number: f1320623
- Front D435 Serial Number: 241122074115
- Back D435 Serial Number: 241222076731

### RP Lidar
- Default baud rate: 115200
- Device appears as: /dev/ttyUSB0 (or similar)

### TI Radar
- Configuration file: /opt/ti-radar/konfigurace.cfg
- Default settings included in the configuration file

## Support
For issues and support:
1. Check the troubleshooting section above
2. Verify all dependencies are correctly installed
3. Ensure proper USB connections and permissions
4. Check system logs for device-related errors:
   ```bash
   dmesg | grep -i usb
   journalctl -f
   ```

## License
[Add your license information here]

## Contributing
[Add contribution guidelines if applicable]

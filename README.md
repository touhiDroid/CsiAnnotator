### Installation Steps:
1. Clone the repository & install necessary libraries:
```shell
git clone https://github.com/touhiDroid/CsiAnnotator.git
cd CsiAnnotator/
pip install -r requirements.txt
```

2. Modify .env
```cp example.env .env
nano .env ## Then modify the `HOST` variable to point to the CSI-Pi server
```

3. Include initial data
```cp data/example-data.json data/data.json
nano data/data.json ## Update this file to contain your initial set of experiments & actions
```

4. Finally, put your image files inside `asset/expt` directory

### For Sound Playback:
```shell
sudo apt update
sudo apt-get install gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly
sudo apt-get install libqt5multimedia5-plugins
```

### Install a Touch-screen Keyboard (Optional, but recommended):
Link: https://docs.sunfounder.com/projects/ts10-pro/en/latest/quick_guide/install_virtual.html
```shell
sudo apt install onboard
sudo apt install at-spi2-core
```
Then, set auto-show options & theme inside `Preferences > Onboard Settings > {General, Window, Auto-show, Layout, Theme}`
### Run the project:
```shell
 sudo chmod +x csi_annotator.sh
 ./csi_annotator.sh
```
Optionally, this script can be added to the OS Menu via `Preferences > Main Menu Editor`, where icon and desktop shortcut can also be defined.

### (Out of Project) Long click as right-click for touch-screens:
```shell
sudo apt install build-essential libevdev2 libevdev-dev
git clone 'https://github.com/PeterCxy/evdev-right-click-emulation.git'
cd 'evdev-right-click-emulation'
```
This codebase has a bug in the `Makefile`. So, change the `Makefile` to this one:
```Makefile
CC := gcc
XFLAGS := -Wall -std=c11 -D_POSIX_C_SOURCE=199309L
LIBRARIES := -levdev
INCLUDES := -I/usr/include/libevdev-1.0
CFLAGS := $(XFLAGS) $(INCLUDES)

OUTDIR := out
SOURCES := uinput.c input.c rce.c
OBJS := $(SOURCES:%.c=$(OUTDIR)/%.o)
TARGET := $(OUTDIR)/evdev-rce

.PHONY: all clean

$(OUTDIR)/%.o: %.c
	@mkdir -p $(OUTDIR)
	$(CC) $(CFLAGS) -c $< -o $@

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) $^ $(LIBRARIES) -o $@

all: $(TARGET)
clean:
	rm -rf $(OUTDIR)
```
Then continue building and
```shell
make all
sudo cp 'out/evdev-rce' '/usr/local/bin/'
sudo chmod +x '/usr/local/bin/evdev-rce'
# Run evdev-rce as normal user
sudo usermod -G 'input' -a pi
echo 'uinput' | sudo tee -a /etc/modules
sudo nano /etc/udev/rules.d/99-uinput.rules
# Then put this line(within backticks): `KERNEL=="uinput", MODE="0660", GROUP="input"`
sudo udevadm control --reload-rules
sudo udevadm trigger
cd
mkdir -p "$HOME/.config/autostart"
nano "$HOME/.config/autostart/evdev-rce.desktop"
```
Then, put this as the desktop entry:
```service
[Desktop Entry]
Version=1.0
Type=Application
Name=evdev-rce
GenericName=Enable long-press-to-right-click gesture
Exec=env LONG_CLICK_INTERVAL=500 LONG_CLICK_FUZZ=50 /usr/local/bin/evdev-rce
Terminal=true
StartupNotify=false
```
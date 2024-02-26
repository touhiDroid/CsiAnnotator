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
PS4 Exploit Host
================

## What is this?
This is an easy way for anyone to host their own exploit for the PS4 on their LAN. Features include:
- Hosts your choice of exploit
- Sends your choice of payload after a successful exploit
- Blocks PSN domains from resolving (Stops accidental updates and block telemetry)
- Serves a specific firmware update to your PS4
- Works on just about every platform

If you do not want to host the package yourself you can use my remote DNS. See the `Using remote DNS` section below.

**PLEASE READ THIS README AND THE [FAQ](https://github.com/Al-Azif/ps4-exploit-host/blob/master/FAQ.md) BEFORE POSTING AN ISSUE.**

## Requirements
- If you are not using a binary release you will need [Python 3](https://www.python.org/downloads/)
- Root privileges on non-Windows machines

## How to download
- Download the zip on the [releases](https://github.com/Al-Azif/ps4-exploit-host/releases) page
- Download with Git, be sure to grab the submodules. This does not include any exploits or payloads. This is for experts only, download a release if you have issues

    `git clone --recursive https://github.com/Al-Azif/ps4-exploit-host.git`

## Using remote DNS (Run Nothing Locally)
0. Make sure the PS4 is on firmware 5.05 or lower (`Settings > System > System Information`).
    - If your firmware version is >5.05 you are out of luck there is no public exploit available and you cannot downgrade.
1. On your PS4 go to `Settings > Network > Setup Network` to setup a network. When you get to DNS Settings select `Manual` and set the Primary to `165.227.83.145` and the Secondary DNS to `108.61.128.158` or visa-versa.
    - If your firmware version is <5.05 you will get a network update available. This is for 5.05.
    - **If you already have an official updated above 5.05 downloaded you must delete it first.**
2. On the PS4, go to `Settings > User's Guide` and select it. The exploit selection should appear.
    - You can also open browser and the default homepage will be the exploit selection.
3. If you use `Original` you will need to use another program to send a payload.

## How to run (Run Locally)
1. Download the files (As shown in the "How to download" section above)
2. Double click the executable (`ps4-exploit-host.exe`, `start.py`, etc). If it starts with no errors, note the IP given
    - Alteratively run it from the command line (`ps4-exploit-host.exe`, `./ps4-exploit-host`, `python start.py`, etc)
    - If you are not root when running on a non-Windows machine you need to use `sudo`
3. On your PS4 `Settings > Network > Setup Network` to setup a network. When you get to DNS Settings select `Manual` and set the Primary and Secondary DNS to the IP address you noted above.
4. Make sure the PS4 is on firmware version 5.05 (`Settings > System > System Information`). If it is not use the jump to the "How to use the Updater" section before continuing
    - If your firmware version is >5.05 you are out of luck there is no public exploit available and you cannot downgrade.
5. On the PS4, go to `Settings > User's Guide` and select it. The exploit should run and there should be output on the script window.
6. If applicable for your exploit the script will prompt you to choose a payload to send. You may send any payload located in the `payloads` folder.
7. When done use `Ctrl+C` to cleanly close the application

Note: You can edit `settings.json` to modify the hosts behavior. There is a section below with more info.

## Running on Raspberry Pi
While the "How to run" section applies to the Pi as well there are some more complex options people may want to use for the Pi like running without any network whatsoever.

- To run as a standalone device that you plug directly into your PS4 though ethernet go [here](https://gist.github.com/Al-Azif/fe2ae67a2fb06cc136580b1e923c7aac) (Supports any Pi with a ethernet port)
- To run as a WiFi access point for your PS4 go [here](https://gist.github.com/Al-Azif/765740019c45b9a49cbf739609cadda7) (Officially supports RPi 3 currently, may work on others with WiFi adapter)

## How to use the built in updater
**If you already have an official updated above 5.05 downloaded you must delete it first.**

0. Follow the "How to run" section until it says to come here
1. Put the system update in the `updates` folder as `PS4UPDATE_SYSTEM.PUP`
    - Optionally put the recovery update in the `updates` folder as `PS4UPDATE_RECOVERY.PUP`

        **5.05 SYS MD5:** F86D4F9D2C049547BD61F942151FFB55

        **5.05 REC MD5:** C2A602174F6B1D8EF599640CD276924A

2. Change the "Update" section in `settings.json` to match your PUP files.
3. MAKE SURE THE DNS IS SET CORRECTLY!
4. **SEE #3 I'M SO SERIOUS!**
5. There should be a different page on the `System Software Update > View Details` option on the PS4. It will be obvious!
    - The PS4 is not using the right DNS if you get the standard Sony changelog page. **STOP IMMEDIATELY AND RESTART THE ENTIRE PROCESS**
6. Run a system update on your PS4 system.
7. Return to the "How to run" section

## Modifying settings.json
It's probably a good idea to make a backup of the default settings.json just in case.

COMING SOON

## Contributing
You can check the [issue tracker](https://github.com/Al-Azif/ps4-exploit-host/issues) for my to do list and/or bugs. Feel free to send a [pull request](https://github.com/Al-Azif/ps4-exploit-host/pulls) for whatever.
Be sure to report any bugs, include as much information as possible.

## What if a new exploit is released?
You should just be able to place the exploit files in the `exploit` directory. The exploit will automatically add the exploit to the menu.

        ex. exploits/firmware_version/exploit_name/index.html

## Why do you commit so many little changes, tweaks, etc?
I have no self control... it also lets people see the actual development. From barely working chicken scratch to actual code.

## Credits
- Specter, IDC, qwertyoruiopz, Flatz, CTurt, Mistawes, XVortex, LightningMods, CelesteBlue123, Anonymous, neofreno, wolfmankurd, crypt0s, etc

Exploit Host
================

## What is this?

This is an easy way for anyone to host their own exploit for the PS4/PS5/Vita/Wii/Switch/etc on their LAN. Features include:

- Hosts your choice of exploit
- Allows caching of exploits for offline use (Device dependant)
- Sends your choice of payload after a successful exploit
- Blocks update/telemetry domains from resolving
- Serves a specific firmware update to your device (Device dependant)
- Server side application works on just about every platform
- Static Website builder. Compiles the host into a static website to run on HTTP server of your choice (You lose some features using this method, DNS, updater, etc)

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

0. Make sure you are on an exploitable device/firmware (ie. PS4: <=9.00, PS5: <=4.51, etc)
    - On the PS4/PS5 this can be found at `Settings > System > System Information`
    - If your firmware is too high you are out of luck there is no public exploit available and you cannot downgrade.
1. On your device go to setup your network as desired but be sure to set the DNS servers to `165.227.83.145` and `192.241.221.79`
    - This is typically found when setting up a "custom" network on the device.
    - Either IP can be used as the Primary or Secondary DNS. Flip a coin to decide. Randomly selecting with help with load balancing.
2. On the device visit the internet. If the devices is explicitly supported the online uses manual, internet connection test, and/or the browsers default homepage should be the exploit page. Examples:
    - On the PS4/PS5, go to `Settings > User's Guide` and select it the exploit selection should appear.
    - On the PS4 uou can also open browser and the default homepage will be the exploit selection.
    - On the Nintendo Switch the internet connection test will be the exploit selection.
3. If you using something like `Bin Loader` you will need to use another program to send the desired payload.

My Twitter is [@_AlAzif](https://twitter.com/_AlAzif) you can check my recent tweets for know issues/maintenance info.

## How to run (Run Locally)

1. Download the files (As shown in the "How to download" section above)
2. Double click the executable (`exploit-host.exe`, `start.py`, etc). If it starts with no errors, note the IP given.
    - Alternatively run it from the command line (`exploit-host.exe`, `./exploit-host`, `python start.py`, etc)
    - If you are not root when running on a non-Windows machine you need to use `sudo`
3. Follow the `Using remote DNS` section substituting your DNS IP given noted in the previous step for both primary and secondary DNS IP addresses.
4. When done use `Ctrl+C` to cleanly close the application.

Note: You can edit `settings.json` to modify the hosts behavior. There is a section below with more info.

## Creating a static HTML build

TBD.

## Running on Raspberry Pi

While the "How to run" section applies to the Pi as well there are some more complex options people may want to use for the Pi like running without any network whatsoever.

- To run as a standalone device that you plug directly into your device though ethernet go [here](https://gist.github.com/Al-Azif/fe2ae67a2fb06cc136580b1e923c7aac) (Supports any Pi with a ethernet port)
- To run as a WiFi access point for your device go [here](https://gist.github.com/Al-Azif/765740019c45b9a49cbf739609cadda7) (Officially supports RPi 3 currently, may work on others with WiFi adapter)

## Running on an ESP device

TBD.

## How to use the built in updater

Below is an example of how to issue the PS4 5.05 update to PS4s that have a lower FW currently installed.

**If you already have an official updated above 5.05 downloaded you must delete it first.**

0. Make these changes before starting the application in the `How to run` section. Look at the `Update [PS4_No_Update]` setting in the `settings.json` info below.
1. Put the system update in the `updates` folder as `PS4UPDATE_SYSTEM.PUP`
    - Optionally put the recovery update in the `updates` folder as `PS4UPDATE_RECOVERY.PUP`

        **5.05 SYS MD5:** F86D4F9D2C049547BD61F942151FFB55

        **5.05 REC MD5:** C2A602174F6B1D8EF599640CD276924A

2. MAKE SURE THE DNS IS SET CORRECTLY!
3. **SEE #2 I'M SO SERIOUS!**
4. There should be a different page on the `System Software Update > View Details` option on the PS4. It will be obvious!
    - The PS4 is not using the right DNS if you get the standard Sony changelog page. **STOP IMMEDIATELY AND RESTART THE ENTIRE PROCESS**
5. Run a system update on your PS4 system.
6. Return to the "How to run" section.

## Modifying `settings.json`

It's probably a good idea to make a backup of the default settings.json just in case. Any invalid settings will throw a warning and use a default value.

Use valid json formatting. Boolean values should be lower case, integers should not be quoted, etc.

| Setting | Notes | Type |
| ------- | ----- | ------- |
| Debug   | Will print debug info from the DNS/HTTP servers | boolean |
| Root_Check | Will skip the root user check for Linux/OSX, only disable if you are sure you don't need it. Will cause port errors if set wrong | boolean |
| Public | If the server is listening on a public IP (Disabled payload sending other than "Auto_Payload and disables viewing/editing settings remotely) | boolean |
| DNS | If the DNS server should be run | boolean |
| HTTP | If the HTTP server should be run | boolean |
| DNS_Interface | The IP of the interface to bind the DNS server to | string (IP Address) |
| DNS_Port | The port to bind the DNS server to | int (1-65535) |
| HTTP_Interface | The IP of the interface to bind the HTTP server to | string (IP Address) |
| HTTP_Port | The port to bind the HTTP server to | int (1-65535) |
| Compression_Level | Enables gzip compression on the HTTP server, 0 being disabled, 9 being most compressed | int (0-9) |
| UA_Check | If the UA should be checked against values in the Valid_UA setting | boolean |
| Theme | Which theme to use, themes must be located in the themes folder | string |
| Sticky_Cache | Whether the appcache manifest should be included in itself or not | boolean |
| Auto_Payload | Payload to send to any IP that accesses server at `/success`. Payload must be in the payloads folder | string |
| Payload_Timeout | The timeout, in seconds, to try and send a payload through the payload menu before timing out | int (1-999) |
| DNS_Rules | Fake DNS control block |  |
| DNS_Rules [Redirect IP] | The IP address to redirect URLs listed in the Redirect rules to | string (IP Address) |
| DNS_Rules [Redirect] | Array of domains to forwards to DNS_Rules [Redirect IP] | array of strings (regex) |
| DNS_Rules [Block] | Array of domains to block | array of strings (regex) |
| DNS_Rules [Pass_Through] | Array of IP addresses to not modify DNS requests | array of strings (IP Address) |
| Valid_UA | User-Agents to allow access to exploits, only used if UA_Check is enabled | array of strings (regex) |
| Update | Updater control block |  |
| Update [PS4_No_Update] | The PS4 version (and lower) listed here will not be served update files | float |
| Update [Vita_No_Update] | The PS Vita version (and lower) listed here will not be served update files | float |

## Modifying metadata

TBD.

## About offline caching

- Redirect/Theme info is cached automatically.
- Redirect/Theme info updates and refreshes automatically.
- Exploits can be cached on a per firmware basis or all cached at once with the dropdown menu and/or `[Cache All]` button on the exploit selection menu.
- Exploit updates must be "manually" updated by clicking cache button an update is available or checking the "About" option in the exploit's dropdown menu.
  - You will be told if there is no update when clicking the button.
- If you are offline the caching buttons will be hidden as will exploits that require a network connection or are not cached.

## About autoload

- Exploits can be automatically selected by clicking "Autoload" in the exploits dropdown menu.
- When you open the exploit selection it'll automatically select that exploit.
- This can be disabled by clearing your browser's cookies.

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

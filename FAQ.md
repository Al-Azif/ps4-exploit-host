PS4 Exploit Host FAQ
====================

**Before seeking help run though the following list:**
- Use the most recent release.
- Follow the directions exactly, do not try to get fancy then come for help.
- If the server starts (It gives you an IP and has not errored out) and you cannot connect from your PS4 (Whitescreen or otherwise), with 99.99% certainty your firewall/anit-virus is blocking it.
- Disable other networking apps that may interfere with the script if you get port errors (Skype, Discord, Torrent Clients, XAMPP, Firewalls, etc).
- It is normal to get some errors (PSN & NAT) while running the network test. This proves the PSN domains are blocked correctly.

**These are NOT related to this script in any way, but rather the exploits/payloads themselves:**
- Make sure your PS4's firmware is on the correct firmware. There is no downgrading.
- The PS4 can get a kernel panic and just shutoff. Physically unplug the power for a second (Or hold the power button for a few seconds), then power it back on.
- "There is not enough free system memory" errors while loading the exploit page are normal, restart your PS4 if you get a lot of them in a row.
- The FTP servers can take a minute to start. Be patient and try again in a 30 seconds.
- The FTP port is 1337.
- You must leave the exploit page open for FTP to work as it runs in the webkit process (Use the PS Button to leave it open in the background)

**Other Notes:**
- Github issues are not for exploit/payload requests.
- Github issues are not for issues with payloads/exploits. They are provided in releases as a convenience.
- Github issues are not for issues with my DNS servers.
- Yes... I know 1/3 anti-virus applications detect this as malware. There are a few reasons for this:
    - The binaries extract files to the temp folder
    - The code, which the AV can see, contains the word 'exploit' and 'payload'
    - The application opens 2 privileged ports (53 & 80) then runs servers on themselves
    - The exploits directory in the releases contain exploits for remote code execution... duh...
    - If you don't trust the binaries, download the python release and use that. You can see all the code as it's a scripting language
    - If you want to help to try to get this white listed contact your anti-virus vendor and submit it to them for analysis. You can also upload it to VirusTotal and comment/vote on it there.
    - If you open a issue about this (Or message me elsewhere about it), I'll close it, block you, and move on with my day. Can you tell I'm tired of the malware comments?

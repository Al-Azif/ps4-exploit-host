Exploit Host FAQ
====================

## Host Related:
**Q: I'm using release X.X.X and...**

A: Use the most recent release.

**Q: I'm following the directions but instead of...**

A: Follow the directions exactly, do not try to get fancy then come for help.

**Q: The server starts but I get a white screen on my device**

A: If the server starts (It gives you an IP and has not errored out) and you cannot connect from your device (Whitescreen or otherwise), with 99.99% certainty your firewall/anti-virus is blocking it.

**Q: I'm getting an error that says another program is running on port X**

A: Disable other networking apps that may interfere with the host (Skype, Discord, Torrent Clients, XAMPP, Firewalls, etc).

**Q: The connection test doesn't pass the PSN & NAT test**

A: It is normal to get some errors (PSN & NAT) while running the network test. This proves the PSN domains are blocked correctly.

**Q: I get an "Error 400: This device is not supported"**

A: The browser's User-Agent checker is enabled and the device is not whitelisted. Disable UA_Check or add the UA in Valid_UA.

**Q: The theme shows up offline but none of the exploits load**

A: The theme is automatically cached (and refreshes automatically when updated). Exploits must be cached manually with either the "[Cache]" or "[Cache All]" buttons.

**Q: I cached the User's Manual and the cache isn't working through the browser (Or visa-versa)**

A: Files are cached for the page you press the button on (User's Manual vs Browser).

**Q: The exploit files I'm running are clearly old versions**

A: When exploit files are changed they must be recached by pressing the button again. It will notify you if there is an update or not when you click the button.

**Q: I connected to another network and the cache no longer works**

A: If you change your network setting the cache will be deleted.

**Q: What does X exploit/payload do?**

A: Visit the About page, located in the header of exploit menu, this includes credits and a short description of each exploit.

**Q: There is a new payload out, when is the next release?**
A: Releases are no longer based on when payloads are created/updated, they are provided in releases as a convenience. You can add/update them yourself. Take a look at the "exploits" folder in a release for the folder structure.

## Firmware, Exploit, and Payload Related:
**Q: I'm on firmware version X.XX, what can I do**

A: As of today you can only exploit consoles firmware version <=5.07. There is no way to downgrade and no ETA for a new exploit.

**Q: Can I play online?**

A: PSN requires the most recent firmware and as such online play does not work. Even if the latest firmware was available you'd be banned instantly from PSN when you connected.

**Q: My device just shut off for now reason after running the exploit/payload**

A: This is called a kernel panic. They are expected and happen randomly. Press and hold the power buttons for a few seconds to restart. It is possible to lose data during a KP if files are being modified, keep a backup. There will be no physical damage to your device, at worst you'll have to completely reinitialize the PS4. Bad news if you're on 5.07 (vs 5.05) as there is no know 5.07 recovery PUP.

**Q: My device keeps saying "There is not enough free system memory"**

A: These are normal, try restarting your device if you get a bunch of them in a row.

**Q: The FTP server isn't starting**

A: It can take a minute to start. Be patient and try again in 30 seconds.

**Q: What's the FTP login info**

A: No Username/Password, port 1337.

**Q: The FTP server isn't staying open**

A: The FTP runs in the WebKit process, you must leave the browser open. Use the PS button to leave it open in the background.

## Other Notes:
- GitHub issues are not for exploit/payload requests.
- GitHub issues are not for issues with payloads/exploits.
- GitHub issues are not for issues with my DNS servers.
- Yes... I know 1/3 anti-virus applications detect this as malware. There are a few reasons for this:
    - The binaries extract files to the temp folder
    - The code, which the AV can see, contains the word 'exploit' and 'payload'
    - The application opens 2 privileged ports (53 & 80) then runs servers on themselves
    - The exploits directory in the releases contain exploits for remote code execution... duh...
    - If you don't trust the binaries, download the python release and use that. You can see all the code as it's a scripting language
    - If you want to help to try to get this white listed contact your anti-virus vendor and submit it to them for analysis. You can also upload it to VirusTotal and comment/vote on it there.

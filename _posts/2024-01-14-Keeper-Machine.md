---
title: Hack The Box - Keeper
date: 2023-01-14 13:33:37 +0200
categories:
  - HackTheBox
tags:
  - HTB
comments: true
---

HTB Keeper Machine - https://www.hackthebox.com/machines/keeper

### Scanning & Enumeration
Scanning the machine first with Nmap tool 
```
nmap -n -Pn -sV 10.10.11.227
```
`22/tcp open ssh OpenSSH 8.9p1 Ubuntu 3ubuntu0.3 (Ubuntu Linux; protocol 2.0)`  
`80/tcp open http nginx 1.18.0 (Ubuntu)`

When open 10.10.11.227:80, it redirect us to `tickets.keeper.htb`, so edit the hosts file:
```
sudo mousepad /etc/hosts
```
`10.10.11.227 keeper.htb`
`10.10.11.227 tickets.keeper.htb`

Lets navigate to it again

![](Pasted%20image%2020260820000528.png)

We can't find any credentials on the source code of the page. So, we can try a couple of default credentials or even look up on the internet for the default creds for Request Tracker.

We can find that the default credentials for this tool are `root: password`. So, we can try that and see if we can gain access to the portal.

The credential worked and we gained access to the portal. So, we can explore different options that are available there and see if we can upload a file somewhere, get a reverse shell, or do a command injection.

### Exploitation & Gaining Access
After spending some time around, we can find a users tab under the Admin section and over there we can see that there is another user named `lnorgaard`. Now, as we have access to the portal as root, we can try to read this user's password or change it.

![](Pasted%20image%2020260820000928.png)

When we click on the user, it gives us all the details as shown below

![](Pasted%20image%2020260820000952.png)

The most interesting part is the comment section, where we can see the plain-text password for this user. Now that we have a pair of username and password, we can try to use them to gain SSH access to the machine.
```
ssh lnorgaard@10.10.11.227
Password: Welcome2023!

lnorgaard@keeper:~$ whoami
lnorgaard@keeper:~$ pwd
lnorgaard@keeper:~$ ls
lnorgaard@keeper:~$ cat user.txt
```

### Privilege Escalation
In order to escalate our privileges, we can start by looking at files are present in the user's directory.
```
ls -lah
```

We can see there is a file called as `RT30000.zip`. We can copy it to our local machine by running the following command and then unzip it:
```
scp lnorgaard@10.10.11.227:~/RT30000.zip /home/kali/Desktop
Password: Welcome2023!

unzip RT30000.zip
file *
```
 `KeePassDumpFull.dmp: Mini DuMP crash report, 16 streams, Fri May 19 13:46:21 2023, 0x1806 type`  
`passcodes.kdbx: Keepass password database 2.x KDBX`  
`RT30000.zip: Zip archive data, at least v2.0 to extract, compression method=deflate`

From the above output it can be seen that we have an application dump file and another Keepass database file. Based on the files that we have.
our approach should be to analyze the dump file to find the master password for the database and then unlock it.

When we investigated KeePass\'s CVE, we found that There was a PoC: <https://github.com/CMEPW/keepass-dump-masterkey> for this CVE-2023-32784 , and the password that can access the kdbx file can be found in the KeePass memory dump file.
```
python3 poc.py -d KeePassDumpFull.dmp
```

![](Pasted%20image%2020260820070710.png)

The confirmed password was broken with special characters (●), making it impossible to confirm accurately, so I did a Google search to infer it and found that the Danish language was broken. Through Googling, I was able to guess it was strawberry cream porridge `rødgrød med fløde` in Danish.

It appears that the `passcodes.kdbx` database can be opened using the obtained password.
As a result of searching for a tool to open it, the tool is provided on the KeePass official website: https://keepass.info/download.html

Using the KeePass program on windows machine, to open `passcodes.kdbx` file with master password: `rødgrød med fløde`

`passcode.kdbx` contains the contents of the ppk file for my root account.
![[Pasted image 20250816234459.png]]

It was possible to copy the contents , save them to a file: key.txt
Then download putty from <https://www.puttygen.com/download.php?val=4> , install it, then go to: `C:\Program Files\PuTTY` and open: `puttygen.exe` , then from: File > Load private key

And follow this steps: <https://www3.wipo.int/confluence/display/wipoimd/Steps+to+convert+private+key+from+putty+format+to+openssh+format>
1. Select the private key which has to be converted to the openssh format and click on Open.
2. Now from the menu click on Conversions→Export OpenSSH key
3. Save the key by clicking on Save to: id_rsa

Exit from the SSH we already have, and connect with the new public key we generated with no password:
```
$ ssh -i id_rsa root@keeper.htb
$ ls
$ cat root.txt
```

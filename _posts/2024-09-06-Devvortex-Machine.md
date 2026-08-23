---
title: Hack The Box - Devvortex
date: 2024-09-06 13:33:37 +0200
categories:
  - HackTheBox
tags:
  - HTB
comments: true
---

HTB Devvortex Machine - https://www.hackthebox.com/machines/devvortex

### Scanning & Enumeration
Scan the machine with Nmap first
```
nmap -sC -sV -v 10.10.11.242 -oN nmap.log
```

`22/tcp open ssh OpenSSH 8.2p1 Ubuntu 4ubuntu0.9 (Ubuntu Linux; protocol 2.0)`  
`| ssh-hostkey:`  
`| 3072 48:ad:d5:b8:3a:9f:bc:be:f7:e8:20:1e:f6:bf:de:ae (RSA)`  
`| 256 b7:89:6c:0b:20:ed:49:b2:c1:86:7c:29:92:74:1c:1f (ECDSA)`  
`|_ 256 18:cd:9d:08:a6:21:a8:b8:b6:f7:9f:8d:40:51:54:fb (ED25519)`  
`80/tcp open http nginx 1.18.0 (Ubuntu)`  
`|_http-title: DevVortex`  
`|_http-server-header: nginx/1.18.0 (Ubuntu)`  
`Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel`

And port 80 is redirecting us to `http://devvortex.htb/`.

So add it to our hosts file: `/etc/hosts`
```
echo "10.10.11.242 devvortex.htb" | sudo tee -a /etc/hosts
```


And navigate to the **devvortex.htb**, to see what we have got

![](/assets/img/posts/Pasted image 20250817003954.png)
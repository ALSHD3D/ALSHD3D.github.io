---
title: Real-World Internal Network Penetration Testing - Authentication Bypass and Unauthenticated Telnet
date: 2026-03-19 13:33:37 +0200
categories: [Penetration Test]
tags: [pentest]     # TAG names should always be lowercase
comments: true
---

### Introduction
During one of my previous internal network penetration testing engagements, several security issues were identified across systems and devices within the internal environment.

This article discusses two findings that demonstrate how seemingly simple misconfigurations can introduce significant security risks:

- An authentication bypass issue affecting the PRTG Traffic Grapher login page.
- An unauthenticated Telnet service exposed by a network printer.

All sensitive information, including client details, IP addresses, hostnames, credentials, and other identifying information, has been removed or redacted.

#### Finding 1: Authentication Bypass in PRTG Traffic Grapher
During the internal network penetration test, a security vulnerability was identified in the **PRTG Traffic Grapher** application.
![](/assets/img/posts/authentication-bypass-unauthenticated-telnet/d1.png)

It was discovered that the application's login page allowed access without providing valid credentials. By submitting the login form with both the username and password fields left empty, it was possible to gain access to the application.
![](/assets/img/posts/authentication-bypass-unauthenticated-telnet/d2.png)

This behavior effectively resulted in an authentication bypass, allowing an unauthenticated user to access the application without valid credentials.

#### Finding 2: Unauthenticated Telnet Service on a Network Printer
During the internal network assessment, it was identified that a network printer exposed the **Telnet service on TCP port 23**.
![](/assets/img/posts/authentication-bypass-unauthenticated-telnet/d3.png)

Telnet is an older remote administration protocol that transmits communication in plaintext. Unlike modern secure management protocols, Telnet does not provide encryption for data transmitted between the client and the device.

Further testing revealed that the service could be accessed without requiring authentication.
![](/assets/img/posts/authentication-bypass-unauthenticated-telnet/d4.png)

It let me to edit the general settings and change the admin password.
![](/assets/img/posts/authentication-bypass-unauthenticated-telnet/d5.png)

Additionally, it exposes valuable info to the attacker to target it.
![](/assets/img/posts/authentication-bypass-unauthenticated-telnet/d6.png)

The presence of an unauthenticated Telnet service could allow an attacker with access to the internal network to interact with the affected printer's management interface or functionality without valid credentials.

### Conclusion
Ultimately, securing an internal network requires more than protecting servers and workstations. Applications, monitoring platforms, printers, and other network-connected devices should all be included within the organization's security strategy.

A simple misconfiguration, weak authentication mechanism, or unnecessary legacy service can provide an attacker with an unexpected path into sensitive systems and information.

---
title: Exposed Credentials Behind a Password Field - A Real-World Pentest Finding
date: 2025-9-03 13:33:37 +0200
categories: [Penetration Test]
tags: [pentest]     # TAG names should always be lowercase
comments: true
---

### Introduction
During one of my previous penetration testing engagements, I identified a sensitive credential exposure issue in an endpoint management application.

### Vulnerability Description
The issue was discovered within the **Endpoint Central**, on the **Software Deployment** functionality, specifically on the **Software Repository** page, where administrators could configure a network share used to store and distribute software packages.

The application displayed the configured network share credentials through a password field. At first glance, the password appeared protected because it was visually masked in the interface.

However, further testing revealed that the password was already available within the client-side page.

### Proof of Concept
By inspecting the page using the browser's developer tools and changing the input field type from `password` to `text`, the masked credential became visible.
![](/assets/img/posts/endpoint-central/7777.png)

This demonstrated that the sensitive credential had been transmitted to and stored within the client-side page, allowing any user with access to the page to reveal it through standard browser functionality.
![](/assets/img/posts/endpoint-central/8888.png)

The exposure of network share credentials poses a significant security risk. Depending on the permissions associated with the account and the accessibility of the network share, an attacker could potentially use the exposed credentials to gain unauthorized access to internal resources, access sensitive files, or move further within the environment.
![](/assets/img/posts/endpoint-central/9999.png)

Access to sensitive configuration pages should be restricted to authorized users.

Additional authentication or privilege verification may also be appropriate before modifying or accessing sensitive configuration settings.

### Conclusion
Ultimately, sensitive credentials should never rely on client-side controls for protection. Security controls such as masked password fields can improve usability and reduce accidental exposure, but they do not provide meaningful protection when the underlying secret has already been sent to the browser.

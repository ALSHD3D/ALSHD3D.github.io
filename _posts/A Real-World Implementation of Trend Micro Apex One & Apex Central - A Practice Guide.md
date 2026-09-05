---
title: A Real-World Implementation of Trend Micro Apex One & Apex Central - A Practice Guide
date: 2025-07-20 13:33:37 +0200
categories: [Network Security]
tags: [network-security,implementation,apex-one,apex-central,trend-micro]     # TAG names should always be lowercase
comments: true
---

In one of my previous engagements as a Network and Security Implementation Engineer, our team worked with a client that required the implementation of Trend Micro security solutions, including Apex One and Apex Central.

The engagement involved the following key activities:
- **Environment Analysis and Solution Design:** Analyze the client's existing environment, technical requirements, and business needs, and implement the security solution based on the approved solution design.
- **Trend Micro Solution Implementation:** Implement and configure Trend Micro Apex One and Apex Central according to security and performance best practices.
- **Knowledge Transfer:** Provide knowledge transfer sessions to the client's IT and security team, covering the deployed solution, its configuration, administration, monitoring, and day-to-day operations.
- **Testing, Monitoring, and Tuning:** Test the implemented solution, monitor its performance and security events, and tune the configuration and policies to ensure optimal security coverage while minimizing unnecessary impact on the environment.
- **Implementation Documentation:** Prepare comprehensive implementation documentation covering the solution architecture, configuration, policies, deployment details, and operational considerations.

This engagement provided practical experience in implementing and configuring enterprise endpoint security solutions based on both:
- Client's business requirements
- Security best practices.

In this blog, I will use this experience as a practical reference while discussing a best-practice approach to implementing Trend Micro Apex One. However, any sensitive client information, internal architecture details, configurations, and other confidential information have been removed or redacted.

I will not focus on the installation process of Trend Micro Apex One, Apex Central, and Smart Protection Server (SPS), as the installation process itself is generally straightforward, and many resources and video tutorials are available that explain how to deploy these solutions.

Instead, this blog will focus on what comes after installation: implementing, and configuring according to security and operational best practices.

Therefore, in this guide, we will take a deeper dive into the implementation process, covering the key considerations, configurations, security policies, and testing, required to build an effective and well-configured Trend Micro endpoint security environment.

### Network Settings
The details are listed here. Always log into Windows as the local administrator.

| VM Name      | Operating System                                                       |
| ------------ | ---------------------------------------------------------------------- |
| VM-DC2016    | Windows Server 2016 (hosting Domain Controller and ApexCentral Server) |
| VM-Server    | Windows Server 2016 (hosting Apex One Server)                          |
| VM-CLIENT-01 | Windows Server 2016                                                    |

### Apex One
**Apex One IP:** `<IP>`
**Number of deployed agents**: 67
**Apex One access:** https://`<IP>:port`/officescan/console
- **Credentials User:** Provided to X team
- **Passwords:** Provided to X team

#### Apex One Dashboard
The Main page of **Apex One** dashboard, will be like that
![](/assets/img/posts/apexone-apexcentral/1.png)

Which it will calculated the unmanaged endpoint, which it is not connect to it yet

#### Apex One License
The product license page will be like that, and depending on the license, it will be valid until 3/2023
![](/assets/img/posts/apexone-apexcentral/2.png)

#### Smart Protection Server Standalone Integration
After that we will integrate Smart Protection Server (SPS), with Apex One, from the **Administration** menu
![](/assets/img/posts/apexone-apexcentral/2.5.png)


We will configure a new standalone Smart Protection Server in the classroom environment and integrate it into the Apex One environment.

##### Access the SPS Management Console 
The Smart Protection Server has been already installed on a virtual machine. you will access the Smart Protection Server Management console and run the Configuration Wizard for first-time installation. 
1. In the VM-Server virtual machine, open Internet Explorer or Chrome and click the Smart Protection 
	Server bookmark or type the following URL to launch the Web console for the Smart Protection 
	Server: https://192.168.4.7:4343.If a Certificate Error message is displayed, accept the Security Exception or Continue to this Website. 
2. The Smart Protection Server Log On window is displayed. 
3. Type the administrator credentials entered during the Smart Protection Server installation and click Log on. 
4. A Welcome window is displayed. Click Configure First Time installation.
![](/assets/img/posts/apexone-apexcentral/3.png)
5. Accept the default selections for the File Reputation Service by clicking Next.
![](/assets/img/posts/apexone-apexcentral/4.png)
6. Accept the default selection for the Web Reputation service by clicking Next.
![](/assets/img/posts/apexone-apexcentral/5.png)
7. Disable Trend Micro Smart Feedback and click Next.
![](/assets/img/posts/apexone-apexcentral/6.png)
8. Leave the proxy settings disabled, and click Finish.
9. The Smart Protection Server Web Management console is displayed.
![](/assets/img/posts/apexone-apexcentral/7.png)

Adding SPS Server to Apex One 
The Smart Protection Server will be identified as a source for Smart Protection information within the Apex One Web Management  console. 
1. Return to the Apex One Web Management console, click Administration > Smart Protection > Smart Protection Sources. 
2. Click the Internal Agents tab, and click the standard list link. 
![](/assets/img/posts/apexone-apexcentral/8.png)
3. In the Standard Smart Protection Server List window, click Add.
![](/assets/img/posts/apexone-apexcentral/9.png)
4. Type the following details for the Smart Protection Server & click Save. 
- Server: 192.168.4.7 
- File Reputation Services: click to enable 
- SSL: click to enable 
- File Reputation Services Port: 443 (click Test Connection and ensure that the connection is successful.) 
- Web Reputation Services: click to enable 
- Web Reputation Services Port: 5274 (Click Test Connection and ensure that the connection is successful.)
![](/assets/img/posts/apexone-apexcentral/10.png)

1. The new Standalone Smart Protection Server is displayed in the Smart Protection Server List. The Smart Protection Servers will be accessed by Agents based on their order in the list & click on Save.
![](/assets/img/posts/apexone-apexcentral/11.png)
2. Click on Save and Notify Agents to distribute the details the Smart Protection Server to the Agents.
![](/assets/img/posts/apexone-apexcentral/12.png)
3. A banner in the console notifies you that Agents are being notified of the new Smart Protection Server.
4. Open Windows Explorer and navigate to the following folder: ...\Apex One\PCCSRV
5. Locate and open the sscfg.ini file to confirm that the Apex One Server is aware of the new Smart Protection Server.
![](/assets/img/posts/apexone-apexcentral/13.png)
6. Open the VM-CLIENT-01 virtual image and in Windows Explorer navigate to the following folder:...\Security Agent.
7. Locate and open the ssnotify.ini file to confirm that the Security Agent is aware of the new Smart Protection Server.
![](/assets/img/posts/apexone-apexcentral/14.png)
8. Close the VM-CLIENT-01 virtual image.

#### Apex One AD Integration
Then it comes the the AD Integration, and it will be synchronized with Apex One too

Apex One will be integrated and synchronized with Microsoft Active Directory to assist in locating endpoint computers. 
1. In the virtual application, click to open the VM-SERVER virtual machine. 
2. Log into Windows Server 2016 with credentials as listed in Network Settings page, if Prompted. 
3. Click on the virtual machine window toolbar to maximize the window. 
	In the Internet Explorer or Chrome Web browser, launch the Apex One Web Management console by typing the following URL: https://`<IP>`:4343/officescan. Alternately, click the Apex One 
	bookmark in the browser, or click Apex One in the Windows Start menu. 
4. Log in with following Apex One credentials when prompted: 
	- User name: root 
	- Password: root 
5. Go to Administration > Active Directory > Active Directory Integration. 
6. Type the name of the classroom domain (trend) and click Save and Synchronize.
![](/assets/img/posts/apexone-apexcentral/15.png)
7. A message in the Web Management console confirms that the Active Directory domains are saved and synchronized.
![](/assets/img/posts/apexone-apexcentral/16.png)

#### SMTP Integration
And we can integrate the SMTP, from the **Administration** menu also
![](/assets/img/posts/apexone-apexcentral/17.png)

#### Integration with Apex Central
Now, we can integrate Apex One is with Apex Central, from the **Administration** menu

Before policies can be deployed through Apex Central, communication between Apex One and Apex Central must be configured. 
1. On the VM-DC2016 image, locate the digital certificate created during the setup of the Apex Central Server. The certificate file is called `TMCM_CA_Cert.pem` and is located in the following folder: 
	`C:\Program Files (x86)\Trend Micro\Control Manager\Certificate\CA\` Copy this file. 
2. On the VM-Server image, log into the Apex One Web Management console and click Administration > Settings > Apex Central. 
3. In the Apex Central Settings window, the Connection Status should be displayed as Not connected.
![](/assets/img/posts/apexone-apexcentral/18.png)

##### Complete the details of Apex Central Server as follows: 
- Entity display name: ApexOne 
- Server FQDN or IP address: dc2016.trend.local 
- Port: Accept the default port of 443 
- Apex Central Certificate: Click Browse and locate the `TMCM_CA_Cert.pem certificate`. 
4.  Click Test connection. A connection was successful message should be displayed. Click OK.
![](/assets/img/posts/apexone-apexcentral/19.png)
5. Click Register. The connection status is updated.
![](/assets/img/posts/apexone-apexcentral/20.png)

**Apex Central Settings** Tab will be like that
![](/assets/img/posts/apexone-apexcentral/21.png)

#### Apex One Scheduled Updates
Now the Agents will scheduled updated from this page, and we can choose to customize it by minutes, hour, daily, or weekly
![](/assets/img/posts/apexone-apexcentral/22.png)


### Apex Central
**Apex Central IP:** `<IP>`
**SMTP enabled.**
**Scheduled reports enabled.**
**Access web console:** https://`<IP>:port`/WebApp/index.html
- **Credentials User:** Provided to X team
- **Passwords:** Provided to X team

#### Apex Central License
The Product of Apex Central is depend on the license you will buy it
![](/assets/img/posts/apexone-apexcentral/23.png)

#### Managing Policies through Apex Central
Before Managing the Policies through Apex Central, ensure that the communication between Apex Central & Apex One is configured. 
##### Create an Apex Central User Account 
An Apex Central administrator account will be created in Apex One. 
1. Still in the Apex One Web Management console, click Administration > Account Management > User Accounts. 
2. Click Add to create a new account. Complete the details for the account as follows:
![](/assets/img/posts/apexone-apexcentral/24.png)

- Select Role: Select Administrator (Built-in) from the list 
- User name: Admin (the name of the Apex Central administrator, created during installation) 
- Description: Apex Central Administrator 
- Password: password (the password of the Apex Central administrator, assigned during installation) 
1. Define the Agent Tree Scope to identify the branches of the Agent Tree this administrator will have control over. The top branch of Apex One Server is selected by default, click Next. 
![](/assets/img/posts/apexone-apexcentral/25.png)
2. To enable the Apex One items that the Apex Central account will have permissions to control, click the
![](/assets/img/posts/apexone-apexcentral/26.png)
3. The new user account is displayed.
![](/assets/img/posts/apexone-apexcentral/27.png)

##### Confirm  Registration 
Confirming the Integration of Apex One and Apex Central by attempting a single sign on into Apex One. 
1. Log into the Apex Central Web Management console by clicking the bookmark in the Internet Explorer or Chrome browser. Log in with the following credentials: 
	- User name: Admin 
	- Password: password
2. Click Administration > Managed Servers > Server Registration. In the Server Type list, click All. Apex One should be listed as a Registered Server. Click the link with the URL.
![](/assets/img/posts/apexone-apexcentral/28.png)

And after the Trend Micro products are registered and integrated with Apex Central, it will look like that
![](/assets/img/posts/apexone-apexcentral/29.png)


3. You should be redirected to the Apex One Web Management console. Since the account for the Apex Central administrator was assigned the Administrator (Built-in) role, they will be logged into Apex One with full access to the Web Management console through single sign- on.

**To Add Apex One to the Product Directory**
1. In the Apex Central Web Management console, click Directories > Products and click Directory Management.
![](/assets/img/posts/apexone-apexcentral/30.png)
2. Click Local Folder, and click Add Folder.
![](/assets/img/posts/apexone-apexcentral/31.png)
3. Type a name for a new folder (or directory), for example, Trend Micro Servers and click Save.
![](/assets/img/posts/apexone-apexcentral/32.png)
4. Expand the New Entity folder. Drag the Apex One Server device (listed as Apex One) from the New Entity folder to the newly created Trend Micro Servers folder & when prompted, click OK to acknowledge the move.
![](/assets/img/posts/apexone-apexcentral/33.png)
5. The Apex One Server should now be displayed in the Trend Micro Servers folder.
![](34.png)

##### Configure Policy Template 
A policy template will be configured to identify the target endpoints receiving the policy details as well as the settings to be deployed to the Security Agents on those endpoints. 
1. Still in the Apex Central Web Management console, click Policies > Policy Management. Click close to hide the information window that is displayed.
![](/assets/img/posts/apexone-apexcentral/35.png)

2. In the Product list, select Apex One Security Agent. To create a policy for this product, click Create or Create one now.
![](/assets/img/posts/apexone-apexcentral/36.png)
3. The policy template window is displayed. From this window, administrators will select the target endpoints and identify the policy settings to be deployed.
![](/assets/img/posts/apexone-apexcentral/37.png)
4. Type a name for the policy, for example, No Scan.
5. Click to enable Specify Target and click Select.
![](/assets/img/posts/apexone-apexcentral/38.png)
6. Click the Browse Tab. Expand DC2016> Local Folder > Trend Micro Servers > Apex One. Click the Trend domain. In the right-hand pane, click to select CLIENT-02.
![](/assets/img/posts/apexone-apexcentral/39.png)
7. Click Add Selected Target then OK.
8. Expand Real-time Scan Settings and click to disable Virus/Malware Scan.
![](/assets/img/posts/apexone-apexcentral/40.png)
9. Scroll down to the bottom of the list and click Deploy.
![](/assets/img/posts/apexone-apexcentral/41.png)
10. The Policy will be listed as Pending while it awaits deployment to the target endpoint Security Agents. It may take some time for the policy to deploy. Click Refresh at the top of the policy list to recheck the status.
![](/assets/img/posts/apexone-apexcentral/42.png)
11. Once applied to the target endpoints, the policy will display with a status of Deployed.

Apex One security agents’ policy created and deployed through Apex Central **Policy Management** tab
![](/assets/img/posts/apexone-apexcentral/43.png)

And we can set the Apex one security agents policy, and enable all policies:
- Application control **enabled**
- Behavior monitoring **enabled**
- Device control **enabled**
- Endpoint Sensor **enabled**
- Manual Scan **enabled**
- Predictive Machine Learning **enabled**
- Real-Time Scan **Enabled**
- Sample Submission to DDA **enabled**
- Smart Scan Method **enabled**
- Scan Now Feature **enabled**
- Scheduled Scan **enabled**
- Suspicious Connection detection and clean **enabled**
- Vulnerability Protection **enabled**
- Web Reputation **enabled**

#### Apex Central AD Integration
Now we can integrated the AD with Apex Central too
![](/assets/img/posts/apexone-apexcentral/44.png)

#### License Management
From the **Administrator** menu, we can see all the TM products license added and deployed in Apex Central **License Management** tab
![](/assets/img/posts/apexone-apexcentral/45.png)
#### Scheduled Updates
We can customize that update, so every 12 hour, it will scheduled
![](/assets/img/posts/apexone-apexcentral/46.png)

In the end, effective endpoint security is not a one-time deployment, it is a continuous process of configuration, monitoring, testing, and optimization to ensure the security solution evolves with the organization's environment and security needs.

---
title: A Real-World Implementation of Trend Micro Deep Security - A Practice Guide
date: 2025-03-14 13:33:37 +0200
categories: [Network Security]
tags: [network-security,implementation,deep-security,trend-micro]     # TAG names should always be lowercase
comments: true
---

### Introduction
In one of my previous engagements as a Network and Security Implementation Engineer, our team worked with a client that required the implementation of Trend Micro security solutions, including Deep Security Manager.

This engagement provided practical experience in implementing and configuring enterprise security solutions based on both:
- The client's business and technical requirements
- Security and operational best practices

In this blog, I will use this experience as a practical reference while discussing a best-practice approach to implementing and configuring Trend Micro Deep Security. However, any sensitive client information, internal architecture details, configurations, and other confidential information have been removed or redacted.

I will not focus on the installation process of Deep Security Manager, as the installation itself is generally straightforward, and many resources and video tutorials are available that explain how to deploy the solution.

Instead, this blog will focus on what comes after installation: properly implementing, configuring, and optimizing the solution according to security and operational best practices.

Therefore, in this guide, we will take a deeper dive into the implementation process, covering key considerations, configurations, security policies, testing, monitoring, and tuning required to build an effective, secure, and well-configured Trend Micro Deep Security environment.

### Network Settings
The details are listed here. Always log into Windows as the local administrator.

| VM Name      | Operating System                                                       |
| ------------ | ---------------------------------------------------------------------- |
| VM-SERVER-01 | Windows Server 2016 (hosting Active Directory)                         |
| VM-SERVER-02 | Windows Server 2016 ( Hosting SQL Server 2016 & Deep Security Manager) |
| VM-SERVER-03 | Windows Server 2012 (Hosting Apex Central)                             |
| VM-SERVER-04 | Windows Server 2019                                                    |

### Deploying Security Agents
Import the Deep Security Agent software into Deep Security Manager 
1. A Deep Security Agent software package will be imported into Deep Security Manager. 
2. Click the VM-SERVER-02 virtual machine in the virtual application, and if prompted, log in to Windows Server 2016 using the credentials as listed in the network settings page. 

**NOTE**: If an Enable Network Discovery message is displayed when logging into ANY virtual machine, click Yes.
![](/assets/img/posts/deep-security/1.png)

3. Double-click the Deep Security Manager shortcut on the Windows Server 2016 desktop and log into the Deep Security Manager Web console with the credentials: 
- **Username**: MasterAdmin 
- **Password**: password 
3. Click the Administration menu. In the left-hand pane, expand Updates > Software > Download Center. 
4. The Trend Micro Download Center is displayed in the right-hand pane of the console, listing all Deep Security Agent software packages available.
![](/assets/img/posts/deep-security/2.png)

Scroll through the list and locate the latest version of the Deep Security Agent for 64-bit Windows: `Agent-Windows-12.0._.x86_64.zip`

6. Click to select the file and click the icon in the Import Now column. Alternately, you can right click the files and click Import from the pop-up menu, or click Import from the menu above the software list.
![](/assets/img/posts/deep-security/3.png)

7. The Deep Security Agent software is downloaded from the Trend Micro Download Center onto the Deep Security Manager server. Once the download is complete, a green check mark will appear in the Imported column. 
8. Under Updates > Software > Local, verify that the Agent software package is listed as having been imported. A green check mark is displayed in the Is Latest column to indicate that the latest version has been imported. 
![](/assets/img/posts/deep-security/4.png)

9. In Windows Explorer, locate the following folder to view the Agent package stored on the Deep Security Manager computer: `C:\Program Files\Trend Micro\Deep Security Manager\Temp\`
![](/assets/img/posts/deep-security/5.png)


10. Open the `Agent-Windows-12.0._.x86_64` folder to view the list components available to install on the Agent computer as Protection Modules are enabled.

#### Export the Deep Security Agent Installer
1. Still on the Local Software page, right-click the 64-bit Windows software package (Agent Windows-12.0.___x64.zip) in the list and click Export Installer.
![](/assets/img/posts/deep-security/6.png)


2. Save the `*.msi` file for the installer to a folder in the desktop.

#### Install Deep Security Agent Manually
A Deep Security Agent will be manually installed on the Windows Server 2016 server hosted on the VM-SERVER-01 virtual machine. 
1. In the virtual application, click the VM-SERVER-01 virtual machine. If prompted, log in to Windows Server 2016 using the credentials as listed in the network settings page. 
2. Previously, the Deep Security Agent installer was exported to a folder in the desktop. A shortcut to this folder has been placed on the desktop of the VM-SERVER-01 image. Double click the shortcut and locate the installer called Agent-Core-Windows 12.0.____.x64.msi. Double-click to start the installation. 
3. Ignore any security warning and click Run to launch the Deep Security Agent Setup Wizard. 
![](/assets/img/posts/deep-security/7.png)

4. The Welcome window is displayed. Click Next.
![](/assets/img/posts/deep-security/8.png)

5. If the terms of the license agreement are acceptable, click I accept the terms in the License Agreement and click next.
![](/assets/img/posts/deep-security/9.png)

6. Accept the default installation folder and click Next.
![](/assets/img/posts/deep-security/10.png)
f11
7. Click Install & a Deep Security Notifier message should be displayed above the system tray.
![](/assets/img/posts/deep-security/12.png)

8. Once complete, click Finish to close the Setup window. Right-click the Deep Security Notifier icon in the system tray and click Open Console. Details of the protection on this computer will be displayed. Note that in this scenario, the Deep Security Agent has not been activated yet, and no protection is being applied.
![](/assets/img/posts/deep-security/13.png)

9. Click Cancel to close the Notifier window. 
10. Close the VM-SERVER-01 virtual machine. 
11. Repeat the Deep Security Agent setup on the Windows Server 2012 machine hosted on the VM-SERVER- 03 image. If prompted, log in to Windows Server 2012 using the credentials as listed in network settings page. 
12. Close the VM-SERVER-03 virtual machine once the installation is complete. 

#### Install a Deep Security Agent using Deployment Script
A Deep Security Agent will be installed on the Windows Server 2019 computer on the VMSERVER- 04 virtual machine using a deployment script. Agent-Initiated Activation must be enabled before the script can be run to insure that the Agent activates properly. In this example, the resulting script will be executed in Windows PowerShell. 
1. Switch to SERVER- 02 Virtual Machine. Return to the Deep Security Manager Web console and click the Administration menu. In the left-hand pane, click System Settings and click the Agents tab. 
2. Click to enable Allow Agent-Initiated Activation and Allow Agent to specify hostname. In the Agent activation token field, type a token for Agent activation, for example, secret and click Save. 
![](/assets/img/posts/deep-security/14.png)

**NOTE**: The Agent activation token insures that only scripts created on this installation of Deep Security Manager are accepted for activation on this installation.

3. At the top of the Deep Security Manager Web console page, click Support > Deployment Scripts. Select Windows Agent Deployment from the Platform list and click to enable Activate Agent automatically after installation. The script is generated and is displayed in the lower frame of the window. Scroll through the script code to examine the commands that are issued when executed.
![](/assets/img/posts/deep-security/15.png)

**NOTE**: The password required for Agent-initiated activation is automatically added to the script. Note the entry “token:secret” near the end of the script.

4. Click Save to File and save the resulting AgentDeploymentScript.ps1 file to the Lab Files folder on the desktop. 
5. Click Close to exit the Deployments Scripts window.
6. In the virtual application, switch to VM-SERVER-04 virtual machine and if prompted, log into Windows Server 2019 using the credentials as listed in network settings page. 
7. Open the Lab Files shortcut on the desktop and locate the script file you saved in the previous step. Right-mouse click the file and click Run with PowerShell. 
![](/assets/img/posts/deep-security/16.png)

8. Click Open. Since the permissions to allow PowerShell scripts to run automatically are not set by default, click Y to execute the script.
![](/assets/img/posts/deep-security/17.png)

The script will execute and the Deep Security Agent will be installed and activated. It may take a couple of minutes for the script to complete since the sleep value in the script will pause the process to allow the Deep Security Agent setup to complete before activating the Agent. Wait for the DSA Deployment Finished message to be displayed in the PowerShell before continuing. 
9. Close the VM-SERVER-04 virtual machine. 

#### Install an Agent using Command Line  
You will install a Deep Security Agent on the VM-SERVER-02 virtual machine. The Deep Security Agent will be installed using a Microsoft Installer command. 
1. Return to the VM-SERVER-02 virtual machine. 
2. copy the Agent-Core-Windows-12.____.x86.msi file to the root of C:\. 
3. Open the Windows Command Prompt from the taskbar and change folders to C:\. 
4. Type the following command and note the name of the Deep Security Agent *.msi file: `dir` 
5. Type the following command to install the Deep Security Agent: `msiexec.exe /q /i <name of Deep Security Agent *.msi file`.
6. This command will install the Deep Security Agent core. 
![](/assets/img/posts/deep-security/18.png)

Since the `/q` switch runs a quiet install, no dialog boxes will be displayed during the installation of the Deep Security Agent, but the Deep Security Notifier icon will appear in the system tray after a few moments. 
Wait until the Notifier icon is displayed in the system tray in the lower right-hand corner of the Windows screen before closing the Command Prompt.


### Configurations
#### Managing Policies

**Creating new policies**  
In this section, participants will be creating new policies  
1. Click Policies > New > New Policy. 
2. Enter the name for the policy as Classroom. If you want the new policy to inherit its settings from an existing policy, select a policy from the Inherit from list. Click Next. 
3. Select whether you want to base this policy on an existing computer's configuration and then click Next. 
4. If you selected Yes in step 3: 
	- Select a computer to use as the basis for the new policy and click Next. 
	- Specify which protection modules will be enabled for the new policy. If this policy is inheriting its settings from an existing policy, those settings will be reflected here. Click Next. 
	- On the next screen, select the properties that you want to carry into the new policy and click Next. Review the configuration and click Finish. 
5. If you selected No in step 3, specify which protection modules will be enabled for the new policy. If this policy is inheriting its settings from an existing policy, those settings will be reflected here. Click Finish. 
6. Click Close. 

#### Deploying Deep Security Relay  
The Deep Security Agent on SERVER-01 will be promoted to become the Relay for the environment. Enable a Deep Security Relay  Relay functionality is enabled by promoting a Deep Security Agent to a Relay. You must have at least one Relay enabled in your environment for software distribution as well as pattern and security updates. 

The Deep Security Agent on the **VM-SERVER-01** virtual machine is already activated. Deep Security Agent will be promoted to become a Relay within the Default Relay Group. 
1. Switch to **VM- Server-02** Still in the Deep Security Manager Web console, click the **Administration** menu. 
2. In the left-hand pane, expand **Updates** and click **Relay Management**. 
![](/assets/img/posts/deep-security/19.png)

3. Click to select the Default Relay Group and click Add Relay.
![](/assets/img/posts/deep-security/20.png)

4. A list of all of the 64-bit Deep Security Agents activated in Deep Security will be displayed. Click to select the SERVER-01 Deep Security Agent computer in the list and click Enable Relay and Add to Group.
![](/assets/img/posts/deep-security/21.png)

The Relay component will be installed and enabled on the Deep Security Agent. This may take a moment to complete.
![](/assets/img/posts/deep-security/22.png)

5. Once the Agent Status is listed as Online, return to the Computers list.
![](/assets/img/posts/deep-security/23.png)

6. The Status column for **SERVER-01** will display a message indicating that a security update is in progress.
![](/assets/img/posts/deep-security/24.png)

This is the Relay retrieving the distributable update components from the Trend Micro ActiveUpdate Server on the Smart Protection Network. Wait for the message to clear before continuing.

7. Hover the pointer over the **SERVER-01** computer in the list, and click **Preview** . The icon for the server in the **Computers** list will be updated to indicate that it is now operating as a Deep Security Relay. The number of components available on the Relay for distribution is also displayed.
![](/assets/img/posts/deep-security/25.png)

A Sending Policy status may also be displayed for other computers in the list as they are advised of the new Relay in their assigned Relay Group.

**NOTE**: A small red icon will be displayed over the computer icon in the Computers list for any Agents promoted to Relays.

### PoC Use Cases
#### Protecting Servers from Malware 
Malware and grayware/spyware scanning will be enabled through the Anti-Malware Protection Module and applied to a server in lab environment though a customized policy. 

##### Create a New Malware Scan Configuration
A new Malware Scan Configuration will be created as a reusable Common Object. 
1. In the virtual application, return to the **VM-SERVER-02** virtual machine, and log into the Deep Security Manager Web console as MasterAdmin. 
2. In the Deep Security Manager Web console, click the **Policies** menu. In the left-hand pane, expand **Common Objects** > **Other** and click **Malware Scan Configurations**. The default Malware Scan Configurations are displayed in the right-hand pane. 
![](/assets/img/posts/deep-security/26.png)

3. Click **New** > **New Real-Time Scan Configuration**. 
4. The Malware Scan Configuration Properties window is displayed. 

Create a new configuration with the following details: 
General tab: 
- **Name**: Type a name for this scan configuration, for example Classroom Scan Configuration 
- Document Exploit Protection: Click to **enable Scan documents for exploits** and **Scan for exploits against known vulnerabilities only**
- **Spyware/Grayware**: Click to Enable Spyware/Grayware protection 
- **Alerts**: Enable to send Alerts when this Malware Scan Configuration logs an event. 
![](/assets/img/posts/deep-security/27.png)

Advanced tab 
- **Remediation Actions**: Custom 
- **Use custom actions**: Set the actions for viruses to Quarantine 
![](/assets/img/posts/deep-security/28.png)

Click OK. 
5. The Malware Scan Configuration is created and added to Common Objects, but has not been applied to any policies or computers yet. 
![](/assets/img/posts/deep-security/29.png)


##### Create a New Policy  
A new policy will be created by duplicating an existing policy and modifying its attributes. 
1. Still in the Deep Security  Manager Web Console, click the Policies menu and in the left-hand pane, click Policies. 
2. Instead of creating a new policy from scratch, we will copy an existing policy and modify some of its attributes. In the right-hand pane, expand Base Policy and click to select the Windows policy. From the menu at the top of the list, click Duplicate. 
![](/assets/img/posts/deep-security/30.png)

A new policy called Windows_2 will be created. 
3. Double-click the Windows_2 policy to display the Details Windows. Rename this policy to **Classroom** and click Save. 
4. In the Policy Details windows, click the Anti-Malware Protection Module in the left-hand frame and set the following on the General tab: 
- Anti-Malware State: On 
- Real-Time Scan: De-select Inherited 
- Malware Scan Configuration: Select the newly created configuration called Classroom Scan Configuration 
- Schedule: Select Every Day All Day 
Click Save. 
![](/assets/img/posts/deep-security/31.png)

##### Apply the Policy to a Computer  
The new policy must be applied to computers to take effect. The new **Classroom** policy will be applied to the Windows Server 2012 computer hosted on the VM-SERVER-03 virtual image. 
1. Still in the console, click the Computers menu to display the computers currently added to Deep Security Manager. 
2. Locate and double-click the SERVER-03 computer to display its details. 
3. From the **Policy** list, select the new **Classroom** policy. Click Save, then Close.
![](/assets/img/posts/deep-security/32.png)


Since this module was not previously enabled, Deep Security Manager executes the installation of the Anti-Malware Protection Module and other required components on this Deep Security Agent. 
4. The Task column for the computer displays Sending Policy. A progress prompt is also displayed as the change is applied. 
![](/assets/img/posts/deep-security/33.png)
5. Security updates will also be applied for the Anti-Malware components. Another progress prompt may be displayed after a moment and the Task column for the computer will change to Security Update in Progress. The updates may take a moment to download.

![](/assets/img/posts/deep-security/34.png)

6. Wait until the Task column clears before continuing. 

7. Hover your mouse over the SERVER-03 computer and click Preview. The Anti-Malware Protection Module now displays as On, with **Real Time** scanning enabled.

**NOTE**: If the Relay was not properly enabled in the previous lab, the Anti-Malware component installation will fail.

##### Blocking Malicious Web Sites  
You will activate the Web Reputation Protection Module in the Classroom policy and attempt to visit potentially hazardous Web sites. Modify a Policy to Activate Web Reputation Policy  
The Web Reputation Protection Module will be enabled in the Classroom policy and sample Web sites will be accessed. 
1. In the virtual application, click the VM-SERVER-02 virtual machine, and sign in to the Deep Security Manager Web console as the Master Admin. 
2. In the Deep Security Manager Web console, click the **Policies** menu. Locate and double-click the Classroom policy to open the Details windows. 
3. Click the **Web Reputation Protection Module** in the left-hand frame and set the following 
General tab 
- Web Reputation State: On 
- Security Level: De-select Inherited and set the level to Medium 
And save.
![](/assets/img/posts/deep-security/35.png)

Advanced tab: 
• Alert: Yes   
Click each of the other tabs to view the different configuration options. 
4. Click Save, then Close. 
5. Deep Security Manager will now deploy the Web Reputation Protection Module to Deep Security Agents using this policy. This may take a few moments. While the installation is in progress, the Task column for SERVER-03 (a computer using the Classroom policy) will display Sending Policy. Once the Task column clears, proceed to the next step. 
6. Click the **Events & Reports** menu. Expand Events and click **System Events** in the left-hand pane and note the entries for the update of the Deep Security Agent on SERVER-03. Doubleclick the entry to view the Details. 
![](/assets/img/posts/deep-security/36.png)

### Integrating Deep Security with Connected Threat 
 We will integrate Deep Security with Deep Discovery Analyzer and Apex Central as part of Connected Threat Defense. A file sample will be submitted manually and the progress of the file through the phases of Connected Threat Defense will be observed.
 
 #### Integrate Deep Security with Apex Central  
To participate in Connected Threat Defense, Deep Security must be added to Apex Central as a Manager Server. 
1. Open the VM-SERVER-02 virtual machine and open the Apex Central Web Management console by typing the following URL, or by clicking the bookmark on the browser toolbar: https://server-03.trend.local:4343/WebApp/Login.html 
2. When prompted, authenticate with the following credentials: 
- **Username**: Admin 
- **Password**: password
1. Click **Administration** > **Managed Servers** > Server **Registration**. 
2. Select Deep Security from the **Server Type** list and click **Add a product**. 
![](/assets/img/posts/deep-security/37.png)

3. Type the details of the Deep Security Manager as follows and click **Save**. 
- **Server**: https://server-02.trend.local:4119 
- **Display name**: Deep Security 
- **User name**: MasterAdmin 
- **Password**: password 
![](/assets/img/posts/deep-security/38.png)

6. Deep Security is now listed as a Managed Server.
![](/assets/img/posts/deep-security/39.png)

Ultimately, implementing Trend Micro Deep Security is not simply a matter of deploying the solution; its effectiveness depends on proper configuration, continuous monitoring, regular testing, and ongoing optimization to ensure it continues to meet the organization's security and operational requirements.

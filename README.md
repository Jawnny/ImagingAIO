# ImagingAIO
The purpose of this project is to create an client imaging environment capable of imaging a machine, logging the machine's hardware information into an inventory spreadsheet, and printing an asset tag for the machine. 

The environment utilizes:
* DRBL/clonezilla for imaging
* VMware to house multiple DRBL servers
* Python to handle the automation
* Thermal printer with 3x1 labels

# Environment Overview
* A VMware host houses DRBL servers as well as the image saving targets
* Image restoration targets are plugged into their respective network(SDA/NVMe/etc.) via IPv4 LAN
* Once a machine finishes imaging it will automatically boot into windows and run two scripts
  * HWreport.ps1 compiles the computer's hardware information and sends it to a network share
  * Get_updates.ps1 initiates a search for windows and driver updates
* The machine hosting the imaging utility software reads the txt sent from newly imaged machines and processes them
* Machine hardware info is saved to an xlsx and an asset tag with SN(+barcode), HWID(+barcode), and essential system info is printed

# Why use a virtual machine image?
While you can use which ever image(s) you'd like, the reasoning for using a VM image is that it is agnostic to computer model. By default there are no drivers installed, which means you won't have to swap images constantly for different machines. While this avoids driver conflicts, it also obviously means your image comes with no drivers. Thus your image should include the get-update.ps1 script which will automatically begin installing any available drivers for the client immediately after booting.

# Installation Guide
This guide is meant to be a rough outline. How you configure the environment will depend on your needs and resources.

# VMware configuration
It is helpful to have more than just one eth interface on your server depending on how many clonezilla servers you plan on running. If you only have one eth interface you will need to configue VLANs on your switch(s) for network segmentation. VLANing is beyond the scope of this guide.
* Install VMware hypervisor on your server
* DRBL servers will be running on the latest distro of Ubuntu so configure your VMs accordingly
  * Each server should have two NICs
    1) Internet access
    2) Client network
  * 1-16GB of RAM depending on expected server load
  * 100GB of storage minimum
* Please refer to: https://drbl.org/installation/ for installing DRBL on your Ubuntu server
* If choosing a VM image then also configure a windows machine(or linux if needed) to be your saved image target
  * Its best to only give it 50GB of storage to keep the primary partiton as small as possible
  * This one should only have a single NIC connected to a server environment. The server will provide NAT/Internet access
* **NVMe and SDA harddrives will require separate servers or images due to how Linux's filesystem treats the different types of drives. Either located in /nvme0n1 or /sda**
# Network configuration
This section will cover your VMware network as well as your physical network topology.
* Configure as many virtual switches as you plan on having DRBL servers + 1 more for internet access
* Add a port group for each VM + 1 more for internet access then assign them to their respective vSwitch
* Per each VM ensure they are connected to both the internet port group and/or their respective client environment port group
* Example of network map: https://i.imgur.com/xWnbR4K.png
# Inventorying client
Any laptop or desktop will work for the inventorying client as long as it is hooked up to a printer(or not if you do not require asset tags) and has Python3 and Adobe Reader(free) installed. Alternatively you can convert the imaging_utility.py into a packaged executable via auto-py-to-exe or a similar program.
* Install Adobe Reader
* Install Python3
* Ensure your directory structure is correct:
  * Image Processing
    * Barcode PDFs
    *  HW_Inventory(this is the network share)
    *  Imaging Reports
    *  Templates
        * Master Template.xlsx
        * Master_Blank.pdf
    * imaging_utility.py
* Run imaging_utility.py
# imaging_utility.py usage
The imaging software is constantly checking the HW_Inventory folder for reports sent by the HWinventory.ps1 script. When a report is received it transcribes the information into a spreadsheet labled with todays date and time as of opening the program. The spreadsheet is saved every time a new report is received so **do not keep the spreadsheet open otherwise it will cause a permissions error.** It then generates a barcode PDF and and prints it using Adobe Reader. The barcode is also archived in Barcode PDFs/current_date in case an asset tag isn't printed for some reason; you can reprint from the archive. 
# HWinventory.ps1 and get_update.ps1 configuration
* Firstly you will need to modify the HWinventory.ps1 script to point to the IP of your network share. This can be found on line 4, 5(cosmetic), 20, and 24.
* The script will wait until it can both ping the network share and google DNS servers to ensure it runs without error. If you would like to run the script without needed internet access simply delete lines 9-12.
* Put the scripts somewhere on your source image.
* Open Registry Editor as admin
* Navigate to: Computer\HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce
* Create a new String Value
* Name the entry "!HWInventory" and "!get-updates" respectively. Note that the "!" deletes the registry entry after being run once.
* For value put: C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -executionpolicy bypass -command " & '[path_to_script]' 


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
# Network configuration
This section will cover your VMware network as well as your physical network topology.
* Configure as many virtual switches as you plan on having DRBL servers + 1 more for internet access
* Add a port group for each VM + 1 more for internet access then assign them to their respective vSwitch
* Per each VM ensure they are connected to both the internet port group and/or their respective client environment port group
# Inventorying client
Any laptop or desktop will work for the inventorying client as long as it is hooked up to a printer(or not if you do not require asset tags) and has Python3 and Adobe Reader(free) installed. Alternatively you can convert the imaging_utility.py into a packaged executable via auto-py-to-exe or a similar program.
* Install Adobe Reader
* Install Python3
* Ensure your directory structure is correct:
  * Image Processing
    * Barcode PDFs
    *  HW_Inventory
    *  Imaging Reports
    *  Templates
        * Master Template.xlsx
        * Master_Blank.pdf
    * imaging_utility.py
* Run imaging_utility.py

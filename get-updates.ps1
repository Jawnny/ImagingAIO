# Creates a directory for logs
New-Item -ItemType directory -Path C:\Drivers -ErrorAction SilentlyContinue

# Install the module "PSWindowsUpdate" from PSGallery
# Then imports the module "PSWindowsUpdate" into Powershell
Install-Module PSWindowsUpdate -Force
Import-Module PSWindowsUpdate -Force

# Cmdlet to install all available drivers and outputs a report to the directory created in step 1
Install-WindowsUpdate -Install -AcceptAll -UpdateType Driver -MicrosoftUpdate -ForceDownload -ForceInstall -IgnoreReboot -ErrorAction SilentlyContinue | Out-File "C:\Drivers\Drivers_Install_1_$(get-date -f dd-MM-yyyy).log" -force

Start-Sleep -Seconds 60
 
# Wait on response from fileserver host
while (-not (Test-Connection -ComputerName 10.68.3.166 -Count 1 -Quiet)) {
    Write-Host "Waiting for connection to 10.68.3.166..."
    Start-Sleep -Seconds 5
 }
 
 while (-not (Test-Connection -ComputerName 8.8.8.8 -Count 1 -Quiet)) {
    Write-Host "Waiting for connection to 8.8.8.8 ..."
    Start-Sleep -Seconds 5
 }
 
# Assigning the variable $biosSerial to Get-ComputerInfo then selecting the property BiosSeralNumber only
# This variable will be used to uniquely name the output .txt file
$biosSerial = (Get-ComputerInfo | select BiosSeralNumber)
 
# Cmdlet Get-ComputerInfo gets computer information then selects only certain properties
# Then it prints the selected properties to a file (The file location in this case is a network share)
Get-ComputerInfo | Select-Object -Property CsManufacturer,CsModel,BiosSeralNumber,CsSystemSKUNumber,OsName,OsVersion,OsArchitecture,CsProcessors,CsNumberOfLogicalProcessors,CsPhyicallyInstalledMemory | Out-File -FilePath "\\10.68.3.166\HW_Inventory2\${biosSerial}.txt"
 
# Cmdlet Get-PhysicalDisk gets storage information then selects only certain properties
# And Finally it appends the information to the original Get-ComputerInfo file generated in the previous step
Get-PhysicalDisk | Select-Object -Property FriendlyName,SerialNumber,MediaType,HealthStatus,Size | Out-File -FilePath "\\10.68.3.166\HW_Inventory2\${biosSerial}.txt" -Append
 
# Create a new form
Add-Type -AssemblyName System.Windows.Forms
$form = New-Object System.Windows.Forms.Form
 
# Set the form properties
$form.Height = 1000
$form.Width = 1000
$form.Text = "Imaging Alert!"
$form.StartPosition = "CenterScreen"
 
# Create a new label 
$label = New-Object System.Windows.Forms.Label
 
# Convert $biosSerial which is a PSObject into a string
# Create a substring of $biosSerial which will only display the actual serial number
$biosSerial = $biosSerial | Out-String
$biosSerial = $biosSerial.substring(20,30)
 
# Set the label properties
$label.Text = "Image Completed!       $biosSerial"
$label.Location = New-Object System.Drawing.Point(10,20)
$label.Height = 650
$label.Width = 700
$label.Font = New-Object System.Drawing.Font("Arial",70,[System.Drawing.FontStyle]::Bold)
 
# Add the label to the form
$form.Controls.Add($label)
 
# Show the form as a dialog
$form.ShowDialog()

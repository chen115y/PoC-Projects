param (
    [string]$endpoint = "",
    [string]$key = "",
    [string]$location = ""
 )

[System.Environment]::SetEnvironmentVariable('azurecognitiveservicesendpoint', $endpoint, [System.EnvironmentVariableTarget]::Machine)
[System.Environment]::SetEnvironmentVariable('azurecognitiveserviceskey', $key, [System.EnvironmentVariableTarget]::Machine)
[System.Environment]::SetEnvironmentVariable('azurecognitiveserviceslocation', $location, [System.EnvironmentVariableTarget]::Machine)

$ProgressPreference = "SilentlyContinue"
$WarningPreference = "SilentlyContinue"
Get-ScheduledTask -TaskName ServerManager | Disable-ScheduledTask -Verbose
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" -Name "HideClock" -Value 1
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" -Name "DisableNotificationCenter" -Value 1
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" -Name "HideSCAVolume" -Value 1

cd C:\
mkdir code
cd code
git clone "https://github.com/ACloudGuru/content-AI-900.git"

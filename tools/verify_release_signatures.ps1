<# Validate the installer, installed launcher and installed Inno uninstaller.
   Run on a clean Windows machine with its default trust store, after installation.
   Does not execute the supplied files or change Windows security settings.
   This checks signatures, not Smart App Control reputation or every runtime DLL.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Installer,
    [Parameter(Mandatory=$true)][string]$InstallDirectory
)
$ErrorActionPreference = 'Stop'
$installRoot = (Resolve-Path -LiteralPath $InstallDirectory).Path
$uninstallers = @(Get-ChildItem -LiteralPath $installRoot -Filter 'unins*.exe' -File)
if ($uninstallers.Count -ne 1) {
    throw "Expected exactly one installed uninstaller, found $($uninstallers.Count)."
}
$files = @(
    (Resolve-Path -LiteralPath $Installer).Path,
    (Join-Path $installRoot 'Dictator.exe'),
    $uninstallers[0].FullName
)
$failures = @()
foreach ($file in $files) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
        $failures += "Missing file: $file"
        continue
    }
    $signature = Get-AuthenticodeSignature -LiteralPath $file
    if ($signature.Status -ne 'Valid') {
        $failures += "$file : $($signature.Status)"
        continue
    }
    if ($signature.SignerCertificate.PublicKey.Oid.Value -ne '1.2.840.113549.1.1.1') {
        $failures += "RSA signing certificate required: $file"
    }
    if ($null -eq $signature.TimeStamperCertificate) {
        $failures += "Missing timestamp: $file"
    }
    [pscustomobject]@{
        File = $file
        Status = $signature.Status
        Publisher = $signature.SignerCertificate.Subject
        SHA256 = (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash
    }
}
if ($failures.Count) { throw ($failures -join [Environment]::NewLine) }
Write-Output 'Signatures passed. Still test install, launch, upgrade and uninstall with Smart App Control enabled.'

# Building and testing on Windows

## Development setup

Use Windows x64 and Python 3.11 x64. From this directory:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -c requirements-lock.txt
.\.venv\Scripts\python.exe -B app.py
```

These are development instructions, not a verified clean-machine build. Upstream
faster-whisper also installs PyAV; this differs from the reviewed PCM-only release.
Do not redistribute an entire development environment without auditing it. Native
dependencies may require Microsoft Visual C++ x64.

Source mode works without Dictator.exe, except Windows autostart requires the compiled
launcher and its runtime/pythonw.exe layout.

## Launcher

```powershell
& "$env:WINDIR\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /nologo /target:winexe /reference:System.Windows.Forms.dll /win32icon:assets\dictator.ico /out:Dictator.exe Dictator.cs
```

The launcher expects runtime/pythonw.exe beside it and executes launcher.py. Keep the
legacy executable name and application identity for upgrade compatibility.

## Installer

Use Inno Setup 6.7.3 with this layout:

```text
parent/
  dictatoro/                         # this source directory
  Dictatoro-0.3-runtime-qt6112-final/      # separately staged runtime
  Dictatoro-0.3-runtime-qt6112-final.cleanup.iss
```

Verify the runtime with tools/build_runtime.py --verify --destination <runtime-folder>.
Compile setup.iss with ISCC. Output goes into the parent directory. /DTESTBUILD creates
an isolated test variant that skips vendor installation and user registry registration;
it must not be distributed as the production installer.

## Bootstrap the distribution from official downloads

Run with Windows x64 Python 3.11 and pip, from the source directory:

```powershell
py -3.11 tools/bootstrap_runtime.py --cache ../download-cache --input ../runtime-input --destination ../Dictatoro-0.3-runtime-qt6112-final
```

Both runtime directories must be new. tools/bootstrap-lock.json pins the official
embedded Python archive and all 30 wheels by URL and SHA-256. The script verifies
every download, installs only those wheels without dependency resolution, and invokes
the trimmed runtime packager. No old application installation is needed. Initial
download requires internet; cached files are hash-checked before reuse.

The bootstrap was exercised on the development computer. A clean Windows installation
with real Intel/Microsoft prerequisites remains a separate release gate. Python 3.11.9
is the existing embedded interpreter baseline; this update does not claim that every
native component is current or free from advisories. See PUBLICATION-CHECKLIST.md.

## Tests

For the current release gates and audit limits, see [RELEASE-READINESS.md](RELEASE-READINESS.md).

Run each tests/test_*.py using a Python environment with the application's dependencies.
These tests mock recording/insertion, isolate their data directories and do not validate
physical microphone quality, actual text insertion or clean-machine installation.
Runtime-specific local tests additionally need the trimmed runtime and model fixtures.


## Include the Base model

Before compiling setup.iss, run `py -3.11 tools/fetch_bundled_base.py`.
This downloads the pinned multilingual Systran/faster-whisper-base revision listed
in tools/bundled-base.json, verifies SHA-256 and stages four files under models/base.
The installed app opens that directory locally; it never runs this download script.
Weights are excluded from Git and the source ZIP. Their source revision, hashes,
model card and MIT attribution are in legal/bundled-base-provenance.json and legal/upstream.
The installer includes Base as a required component and removes it on uninstall.
Downloaded optional models remain in the separate user-data cache under the existing policy.
Run tests/test_bundled_base.py --require-bundled to verify actual offline loading/inference.

## Signed Windows release (required for the reported Smart App Control block)

The existing Base Preview installer is unsigned. On a second computer Windows blocked
its generated unins000.exe, preventing both app-menu and Windows-settings removal.
Rebuilding the unsigned preview does not resolve this. Do not disable Smart App Control
or install a self-signed root certificate as a release workaround.

Configure the Inno Setup signing tool named `dictatoro_release` with an approved signing
provider. Use a publicly trusted RSA code-signing certificate, SHA-256 file signing and
an RFC3161 SHA-256 timestamp from the provider. Keep credentials outside the repository.
The signing command must return failure when signing fails. It must include Inno's `$f`
placeholder for the filename. Use Inno's Configure Sign Tools dialog or its `/S` option.

Compile `ISCC.exe /DSIGNEDRELEASE setup.iss`. This mode signs Dictator.exe using the
Files `sign` flag, and signs both Setup and its generated uninstaller with SignTool and
SignedUninstaller=yes. The output is `Dictatoro-0.3-Base-Signed-Setup.exe`; preview and
test names stay distinct. Without the configured tool, compilation must fail.
Do not modify signed executables after signing. Do not publish cached signed Inno
uninstaller files as standalone removal tools: use the matching full installer.

After installing into a test directory on a Windows machine with a default trust store:

```powershell
./tools/verify_release_signatures.ps1 -Installer ../Dictatoro-0.3-Base-Signed-Setup.exe -InstallDirectory 'C:\Dictatoro-test'
```

The verifier requires valid RSA signatures and timestamps for the installer, installed
launcher and installed uninstaller. Local trust validation is not a replacement for
public certificate provenance or Smart App Control testing. Test fresh install and
upgrade over the unsigned preview, then uninstall via Windows Settings with Smart App
Control enabled. Also inspect blocked runtime DLLs, if any. A passing signature check
does not guarantee SmartScreen reputation or trust for every third-party component.
No trusted signing credential was available when this mode was added; signed build and
clean-machine Smart App Control checks remain pending.

References: https://jrsoftware.org/ishelp/topic_setup_signeduninstaller.htm and
https://learn.microsoft.com/en-us/windows/apps/develop/smart-app-control/code-signing-for-smart-app-control

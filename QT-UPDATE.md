# Qt 6.11.2 candidate — 2026-09-24

This candidate replaces Qt/PySide/Shiboken 6.8.3 with 6.11.2. The interface and
recognition settings are unchanged. It is a preview, not a security certification.

## Packaging

- Downloaded all 30 wheels from PyPI and checked publisher SHA-256 values.
- Downloaded embedded Python 3.11.9 from python.org; its executable's Windows
  Authenticode signature verified as Python Software Foundation. The archive hash
  is pinned in tools/bootstrap-lock.json for subsequent builds.
- Added tools/bootstrap_runtime.py; it needs standard Windows x64 Python 3.11/pip
  as a build tool, but does not copy the old application runtime.
- Built twice from separately prepared inputs. All 2,930 retained files matched by
  SHA-256 after stripping developer launchers/local wheel URLs and normalizing RECORD.
- Downloaded matching Qt Base and PySide source archives and verified publisher
  SHA-256 values. Updated notices, dependency inventory and legal manifest.
- Kept exact-path cleanup rules for legacy runtime and legal files during upgrade.

## Validation

- Five application regression scripts passed on the candidate runtime.
- All three pages passed layout checks in eight languages at 100%, 150% and 200% scale.
- Real local Tiny inference, VAD, audio resampling and native Windows mouse hook
  lifecycle passed. No microphone audio was recorded.
- Installed the preceding Qt 6.8.3 test build, upgraded to this candidate, verified
  2,929 installed runtime files and 192 legal files, ran the startup check using an
  external Intel DLL, upgraded again and uninstalled. All checks passed; an unrelated
  file survived uninstall. MIT and the gold icon were installed.
- The isolated installer test skips actual Intel/Microsoft installation and user
  registry registration; Intel MSI discovery is mocked. It is not a clean Windows test.

## Security scope and remaining work

The Qt 6.8.3 version associated with the previously identified Markdown/data URL/color
profile advisories is no longer shipped. Qt 6.11.2 also fixes
[CVE-2026-78253](https://www.qt.io/blog/security-advisory-cve-2026-78253).
This is not an exhaustive audit of all Python/native dependencies. Python 3.11.9 and
the recognition dependencies retain their existing versions and need continued review.

No Windows Sandbox, VirtualBox or VMware command was available in this environment.
Actual clean-system prerequisite installation, Windows startup/shortcuts, cancellation,
restart and manual dictation across physical microphones still need verification.
The candidate remains unsigned. No repository or release was published by this work.

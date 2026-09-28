# Publication review — 2026-09-24

Status: Qt 6.11.2 source publication candidate; binary release is NOT approved as a stable release.
No GitHub repository has been created or uploaded by this review.

Latest status (2026-09-25): see [RELEASE-READINESS.md](RELEASE-READINESS.md).
It supersedes older aggregate test counts and records the native dependency review,
actual Qt 6.8.3 upgrade test and unresolved signing/Smart App Control issue.

## Completed

- MIT license for Dictatoro code, authorized by the maintainer; third-party terms retained.
- Refreshed README, build/runtime documentation, contributor and security-report instructions.
- Project story updated in all eight interface languages; paid-price and certification/Mac promises removed.
- Known credential-pattern and private-data filename scan of publication files: no findings after local paths were redacted.
- No local Git history exists to scan. Remote website repository/history is outside this review.
- Dependency lock agrees with all 30 packages in the staged runtime and license inventory.
- Runtime and legal file manifest hashes verified.
- UI geometry checked at 680x500 logical pixels, all three pages in eight languages.
- Model-cache switching, translation, recording-error handling, focus guard and new failure regressions passed.
- Real local Tiny inference, VAD, resampling and native mouse hook lifecycle passed. No user audio was recorded.
- Rebuilt the trimmed runtime from the existing local source runtime, and compiled launcher and installer.
- Isolated install, upgrade and uninstall passed; 2,857 runtime files and 192 legal files matched hashes.
- MIT license and gold icon installed; legacy OpenMP DLL excluded/removed; unrelated file preserved on uninstall.
- Publisher-hashed PyPI wheels matched 40 retained native files across PySide6 Essentials, Shiboken6, CTranslate2, ONNX Runtime and NumPy.
- OSV query for the 30 pinned PyPI packages returned no advisories on the review date. This is not a clean bill of health for native dependencies.

## Release gates still open

1. **Qt update completed in this candidate.** Qt/PySide/Shiboken are now 6.11.2.
   Matching Qt Base and PySide source archives were downloaded with publisher SHA-256
   verification, and notices refreshed. The previously listed 2025 advisories affect
   the old 6.8.3 build. Qt 6.11.2 also fixes CVE-2026-78253 according to
   https://www.qt.io/blog/security-advisory-cve-2026-78253.
   This is not a blanket claim about every native dependency.
2. **Pinned bootstrap implemented.** tools/bootstrap_runtime.py uses only the official
   inputs in bootstrap-lock.json, with SHA-256 checks. It does not copy the old runtime.
   This was tested in new folders on this computer; it is not a clean Windows VM test.
3. **Clean Windows installation.** The isolated test skipped vendor installation and mocked Intel MSI discovery.
   Verify actual Intel/Microsoft installation, cancellation/restart, real shortcuts, startup registry,
   installation into a custom directory, old-version upgrade and uninstall on a clean VM or PC.
4. **Native license completeness.** Source archives, dynamic Qt libraries and replacement instructions are supplied.
   Confirm final native/transitive dependency notices and binary-to-source/build provenance for the candidate.
   Matching five publisher wheels is evidence of origin, not a legal compliance certificate.
5. **Manual usability.** Test real keyboard/mouse dictation and paste in multiple applications,
   physical microphones, noisy/quiet speech, display scaling and keyboard layouts. Existing automated
   dispatch tests and benchmark samples do not replace these checks.
6. **Public project identity.** Create the separate project repository, add its verified URL to About/README,
   attach reviewed release artifacts and explain that Windows signatures are not yet present.

## Fixes from this review

- Refuse automatic insertion when the foreground process identity is unknown.
- Restore the selected language and persisted configuration after a save/registry failure.
- Preserve error reporting and exit cleanup when a disconnected microphone also fails to close.
- Accept malformed language settings safely.
- Isolate the UI regression test from real Windows language preferences.

Do not claim the application has no vulnerabilities, that licensing is fully certified,
or that a clean Windows installation has already been tested.

**Blocking field report (2026-09-25):** Smart App Control blocked the unsigned
unins000.exe on another computer. Both uninstall entry points therefore failed.
The SIGNEDRELEASE build mode now supports signing Setup, Uninstall and Dictator.exe,
but no signing certificate/provider is configured yet. Before claiming this resolved,
produce the signed artifact, run tools/verify_release_signatures.ps1, and test fresh
install plus upgrade/uninstall on Windows with Smart App Control enabled. Existing
automated uninstall tests did not cover that policy and are not evidence of a fix.

The Completed list above records the preceding audit; current Qt-update test results
are recorded in QT-UPDATE.md. Existing recognition settings were not retuned.

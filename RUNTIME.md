# Runtime packaging for Dictatoro 0.3

setup.iss uses the sibling directory Dictatoro-0.3-runtime-qt6112-final and the generated
Dictatoro-0.3-runtime-qt6112-final.cleanup.iss. It does not install dependencies from pip.

The packager tools/build_runtime.py accepts an existing Windows x64 embedded Python
3.11 runtime as --source and a NEW folder as --destination. Review the source
runtime's origin and locked package versions before using it. The reviewed staging
runtime uses Python 3.11.9 and the versions in requirements-lock.txt.

The script keeps Qt Core/GUI/Widgets and required plugins; removes unused Qt modules,
PyAV/FFmpeg, ASIO, cuDNN and packaging tools; and applies the PCM-only faster-whisper
change in legal/faster-whisper-pcm.patch. File decoding is unsupported in this build.

Staging retains a legacy Intel OpenMP DLL for local tests, but setup.iss explicitly
excludes every libiomp5md.dll from the installer. Installed Dictatoro discovers and
loads Intel Runtime 2025.2.1 installed separately. Microsoft VC++ files are excluded
and obtained from Microsoft. Intel MKL embedded in CTranslate2 has separate notices.

runtime-manifest.json records retained hashes, removed paths and modifications.
--verify checks it and regenerates the exact-file upgrade cleanup list. This manifest
is a packaging check, not a restriction on user replacement of LGPL libraries.

Corresponding source archives and notices in legal/ are installed as mandatory files.
After dependency changes, review versions, source provenance, notices, hashes,
cleanup rules and the actual installed file set together.

tools/bootstrap_runtime.py now builds from pinned official Python/wheel downloads.
The bootstrap is tested in a new folder on the development computer. Testing on a
clean Windows system, and review of remaining native/transitive dependencies, remain
separate release gates. Qt/PySide/Shiboken use version 6.11.2.

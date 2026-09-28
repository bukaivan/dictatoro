#define AppVersion "0.3"
#if defined(SIGNEDRELEASE) && defined(TESTBUILD)
  #error SIGNEDRELEASE cannot be combined with TESTBUILD
#endif
#include "legacy-runtime-cleanup.iss"
#include "..\Dictatoro-0.3-runtime-qt6112-final.cleanup.iss"
#ifdef TESTBUILD
  #define AppIdentity "Dictator.IsolatedInstallerTest"
  #define RegistryBase "Software\DictatorInstallerTest"
  #define RunName "DictatorInstallerTest"
  #define OutputName "Dictatoro-0.3-Base-TestSetup"
#else
  #define AppIdentity "Dictator.Desktop"
  #define RegistryBase "Software\Dictator"
  #define RunName "Dictator"
  #ifdef SIGNEDRELEASE
    #define OutputName "Dictatoro-0.3-Base-Signed-Setup"
  #else
    #define OutputName "Dictatoro-0.3-Base-Preview-Setup"
  #endif
#endif

[Setup]
AppId={#AppIdentity}
AppName=Dictatoro
AppVersion={#AppVersion}
AppVerName=Dictatoro {#AppVersion}
AppPublisher=Dictatoro
DefaultDirName={code:DefaultDirectory}
DefaultGroupName=Dictatoro
DisableDirPage=no
DisableProgramGroupPage=yes
DisableWelcomePage=no
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.17763
#ifdef TESTBUILD
AppMutex=Local\Dictator.InstallerTest.Singleton
CreateUninstallRegKey=no
#else
AppMutex=Local\Diktatoro.Singleton
#endif
CloseApplications=no
RestartApplications=no
OutputDir=..
OutputBaseFilename={#OutputName}
SetupIconFile=assets\dictator.ico
UninstallDisplayIcon={app}\Dictator.exe
UninstallDisplayName=Dictatoro {#AppVersion}
Compression=lzma2/fast
SolidCompression=yes
WizardStyle=modern
ShowLanguageDialog=yes
LanguageDetectionMethod=uilanguage
UsePreviousLanguage=no
ChangesAssociations=no
SetupLogging=yes
#ifdef SIGNEDRELEASE
; Configure this named tool externally; never put signing credentials in source.
SignTool=dictatoro_release
SignedUninstaller=yes
SignToolRetryCount=2
#endif

[Languages]
Name: "ru"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "pl"; MessagesFile: "compiler:Languages\Polish.isl"
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "de"; MessagesFile: "compiler:Languages\German.isl"

[CustomMessages]
ru.CustomInstallation=Выборочная установка
en.CustomInstallation=Custom installation
pl.CustomInstallation=Instalacja niestandardowa
es.CustomInstallation=Instalación personalizada
de.CustomInstallation=Benutzerdefinierte Installation
ru.Standard=Обычная установка
en.Standard=Standard installation
pl.Standard=Instalacja standardowa
es.Standard=Instalación estándar
de.Standard=Standardinstallation
ru.Core=Dictatoro, локальное распознавание и встроенные библиотеки (обязательно)
en.Core=Dictatoro, local speech recognition and bundled libraries (required)
pl.Core=Dictatoro, lokalne rozpoznawanie mowy i biblioteki (wymagane)
es.Core=Dictatoro, reconocimiento local y bibliotecas incluidas (obligatorio)
de.Core=Dictatoro, lokale Spracherkennung und Bibliotheken (erforderlich)
ru.Docs=Инструкция и список компонентов
en.Docs=User guide and component list
pl.Docs=Instrukcja i lista składników
es.Docs=Guía y lista de componentes
de.Docs=Anleitung und Komponentenliste
ru.Startup=Запускать Dictator при входе в Windows (в трее)
en.Startup=Start Dictator at Windows sign-in (in tray)
pl.Startup=Uruchamiaj Dictator przy logowaniu do Windows (w zasobniku)
es.Startup=Iniciar Dictator al entrar en Windows (en la bandeja)
de.Startup=Dictator bei Windows-Anmeldung starten (im Infobereich)
ru.Intro=Локальный голосовой ввод
en.Intro=Local voice typing
pl.Intro=Lokalne dyktowanie
es.Intro=Dictado local
de.Intro=Lokale Spracheingabe
ru.Details=В комплект входят приложение, Python, Whisper и библиотеки. Модель Base уже включена: после установки можно сразу диктовать без скачивания модели. Другие модели загружаются по желанию.%n%nЕсли Microsoft Visual C++ отсутствует или устарел, установщик скачает официальный компонент с сайта Microsoft и предложит установить его. Для скачивания нужен интернет. Для этого Windows может запросить права администратора.%n%nВыбранный язык установки станет языком интерфейса Dictatoro. Позже его можно изменить в настройках.%n%nIntel OpenMP устанавливается отдельно с сайта Intel (~189 МБ). Его установщик покажет собственные условия и может запросить права администратора. Требуется интернет.
en.Details=Includes the app, Python, Whisper and libraries. Base is included and ready after installation, without a model download. Other models are optional downloads.%n%nIf Microsoft Visual C++ is missing or outdated, Setup downloads the official package directly from Microsoft and opens its installer. Internet is required for this download. Windows may request administrator permission for this component.%n%nThe installation language becomes the Dictatoro interface language. You can change it later in Settings.%n%nIntel OpenMP is installed separately from Intel (~189 MB). Its installer displays its own terms and may request administrator permission. Internet is required.
pl.Details=Pakiet zawiera aplikację, Python, Whisper i biblioteki. Model Base jest dołączony i działa od razu po instalacji, bez pobierania. Inne modele można pobrać opcjonalnie.%n%nJeśli Microsoft Visual C++ nie jest zainstalowany lub jest nieaktualny, instalator pobierze oficjalny pakiet bezpośrednio od Microsoft i otworzy jego instalator. Pobieranie wymaga internetu. Windows może poprosić o uprawnienia administratora.%n%nJęzyk instalacji będzie językiem interfejsu Dictatoro. Można go zmienić w ustawieniach.%n%nIntel OpenMP jest instalowany osobno z witryny Intel (~189 MB). Instalator wyświetla własne warunki i może wymagać uprawnień administratora. Wymagany jest internet.
es.Details=Incluye la aplicación, Python, Whisper y bibliotecas. Base está incluido y funciona tras la instalación, sin descargar el modelo. Los demás modelos se descargan opcionalmente.%n%nSi falta Microsoft Visual C++ o está desactualizado, se descargará el paquete oficial directamente de Microsoft y se abrirá su instalador. La descarga requiere internet. Windows puede solicitar permisos de administrador.%n%nEl idioma de instalación será el de la interfaz de Dictatoro. Puedes cambiarlo en Ajustes.%n%nIntel OpenMP se instala por separado desde Intel (~189 MB). Su instalador muestra sus condiciones y puede solicitar permisos de administrador. Se requiere internet.
de.Details=Enthält die App, Python, Whisper und Bibliotheken. Base ist enthalten und nach der Installation ohne Modelldownload nutzbar. Weitere Modelle können optional heruntergeladen werden.%n%nWenn Microsoft Visual C++ fehlt oder veraltet ist, lädt Setup das offizielle Paket direkt von Microsoft herunter und öffnet dessen Installer. Dafür ist Internet erforderlich. Windows kann dafür Administratorrechte anfordern.%n%nDie Installationssprache wird als Dictator-Oberflächensprache verwendet. Sie kann später in den Einstellungen geändert werden.%n%nIntel OpenMP wird separat von Intel installiert (~189 MB). Der Installer zeigt eigene Bedingungen und kann Administratorrechte anfordern. Internet ist erforderlich.
ru.VCError=Не удалось установить Microsoft Visual C++ x64. Разрешите установку компонента и повторите попытку. Код: 
en.VCError=Microsoft Visual C++ x64 could not be installed. Allow the component installation and retry. Code: 
pl.VCError=Nie można zainstalować Microsoft Visual C++ x64. Zezwól na instalację składnika i spróbuj ponownie. Kod: 
es.VCError=No se pudo instalar Microsoft Visual C++ x64. Permite la instalación y vuelve a intentarlo. Código: 
de.VCError=Microsoft Visual C++ x64 konnte nicht installiert werden. Installation zulassen und erneut versuchen. Code: 
ru.CheckError=Проверка запуска не прошла. Подробности: %LOCALAPPDATA%\Diktatoro\startup-error.log. Установка сохранена для исправления или удаления.
en.CheckError=Startup check failed. Details: %LOCALAPPDATA%\Diktatoro\startup-error.log. Installation is retained for repair or removal.
pl.CheckError=Test uruchamiania nie powiódł się. Szczegóły: %LOCALAPPDATA%\Diktatoro\startup-error.log. Instalację zachowano do naprawy lub usunięcia.
es.CheckError=Falló la comprobación de inicio. Detalles: %LOCALAPPDATA%\Diktatoro\startup-error.log. La instalación se conserva para repararla o eliminarla.
de.CheckError=Startprüfung fehlgeschlagen. Details: %LOCALAPPDATA%\Diktatoro\startup-error.log. Die Installation bleibt zur Reparatur oder Entfernung erhalten.
ru.RemoveData=Удалить также скачанные модели, настройки и журналы Dictator?%n%nНажмите «Нет», чтобы сохранить их для повторной установки.
en.RemoveData=Also delete downloaded models, settings and Dictator logs?%n%nChoose No to keep them for reinstallation.
pl.RemoveData=Usunąć również pobrane modele, ustawienia i dzienniki Dictator?%n%nWybierz Nie, aby zachować je do ponownej instalacji.
es.RemoveData=¿Eliminar también los modelos descargados, los ajustes y los registros de Dictator?%n%nElige No para conservarlos para una reinstalación.
de.RemoveData=Auch heruntergeladene Modelle, Einstellungen und Dictator-Protokolle löschen?%n%nNein wählen, um sie für eine Neuinstallation zu behalten.
ru.RemoveProgram=Удалить Dictator
en.RemoveProgram=Uninstall Dictator
pl.RemoveProgram=Odinstaluj Dictator
es.RemoveProgram=Desinstalar Dictator
de.RemoveProgram=Dictator deinstallieren

[Types]
Name: "standard"; Description: "{cm:Standard}"
Name: "custom"; Description: "{cm:CustomInstallation}"; Flags: iscustom
[Components]
Name: "core"; Description: "{cm:Core}"; Types: standard custom; Flags: fixed
Name: "docs"; Description: "{cm:Docs}"; Types: standard
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; Flags: unchecked
Name: "startup"; Description: "{cm:Startup}"; Flags: unchecked
[Files]
#ifdef SIGNEDRELEASE
Source: "Dictator.exe"; DestDir: "{app}"; Flags: ignoreversion sign; Components: core
#else
Source: "Dictator.exe"; DestDir: "{app}"; Flags: ignoreversion; Components: core
#endif
Source: "*.py"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "translations.json"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "models\base\config.json"; DestDir: "{app}\models\base"; Flags: ignoreversion; Components: core
Source: "models\base\model.bin"; DestDir: "{app}\models\base"; Flags: ignoreversion; Components: core
Source: "models\base\tokenizer.json"; DestDir: "{app}\models\base"; Flags: ignoreversion; Components: core
Source: "models\base\vocabulary.txt"; DestDir: "{app}\models\base"; Flags: ignoreversion; Components: core
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs; Components: core
Source: "..\Dictatoro-0.3-runtime-qt6112-final\*"; DestDir: "{app}\runtime"; Excludes: "__pycache__\*,*.pyc,libiomp5md.dll,runtime-manifest.json"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core
Source: "legal\*"; DestDir: "{app}\legal"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion; Components: docs
Source: "requirements*.txt"; DestDir: "{app}"; Flags: ignoreversion; Components: docs

[InstallDelete]
Type: files; Name: "{app}\runtime\Lib\site-packages\ctranslate2\libiomp5md.dll"
Type: files; Name: "{app}\runtime\runtime-manifest.json"

[CustomMessages]
ru.IntelError=Не удалось установить Intel Runtime. Запустите установщик в обычном режиме, завершите установку Intel и повторите попытку. 
en.IntelError=Intel Runtime installation failed. Run Setup interactively, complete the Intel installation and retry. 
pl.IntelError=Instalacja Intel Runtime nie powiodła się. Uruchom instalator interaktywnie, zakończ instalację Intel i spróbuj ponownie. 
es.IntelError=No se pudo instalar Intel Runtime. Ejecuta el instalador de forma interactiva, completa la instalación de Intel y vuelve a intentarlo. 
de.IntelError=Intel Runtime konnte nicht installiert werden. Setup interaktiv starten, die Intel-Installation abschließen und erneut versuchen. 
[Icons]
#ifdef TESTBUILD
Name: "{app}\TestShortcuts\Dictator"; Filename: "{app}\Dictator.exe"; WorkingDir: "{app}"; IconFilename: "{app}\assets\dictatoro-gold.ico"
Name: "{app}\TestShortcuts\Uninstall Dictator"; Filename: "{uninstallexe}"
#else
Name: "{group}\Dictatoro"; Filename: "{app}\Dictator.exe"; WorkingDir: "{app}"; IconFilename: "{app}\assets\dictatoro-gold.ico"; AppUserModelID: "Dictator.Desktop"
Name: "{group}\{cm:RemoveProgram}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Dictatoro"; Filename: "{app}\Dictator.exe"; WorkingDir: "{app}"; IconFilename: "{app}\assets\dictatoro-gold.ico"; Check: ShouldCreateDesktopIcon; AppUserModelID: "Dictator.Desktop"
#endif
[Registry]
#ifndef TESTBUILD
Root: HKCU; Subkey: "{#RegistryBase}"; ValueType: string; ValueName: "UILanguage"; ValueData: "{language}"; Flags: uninsdeletevalue uninsdeletekeyifempty
Root: HKCU; Subkey: "{#RegistryBase}"; ValueType: string; ValueName: "InstallDir"; ValueData: "{app}"; Flags: uninsdeletevalue uninsdeletekeyifempty
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#RunName}"; ValueData: """{app}\Dictator.exe"" --startup"; Tasks: startup; Flags: uninsdeletevalue
#endif
[Run]
Filename: "{app}\Dictator.exe"; Description: "{cm:LaunchProgram,Dictatoro}"; Flags: nowait postinstall skipifsilent; Check: StartupCheckPassed

[Code]
function ShouldCreateDesktopIcon: Boolean;
begin
  Result := WizardIsTaskSelected('desktopicon') or FileExists(ExpandConstant('{autodesktop}\Dictatoro.lnk'));
end;

function MsiGetComponentPath(ProductCode, ComponentCode, Path: String; var Size: Cardinal): Integer;
  external 'MsiGetComponentPathW@msi.dll stdcall';

function IntelInstalled: Boolean;
var Path: String; Size: Cardinal;
begin
  Size := 32768;
  SetLength(Path, Size);
  Result := MsiGetComponentPath('{0C8A072B-5439-4421-B569-0AB7D14F0005}',
    '{CC95C88A-4143-4039-B3D2-AB68D333B651}', Path, Size) = 3;
  if Result then begin
    SetLength(Path, Size);
    Result := FileExists(Path);
  end;
end;

var
  CheckPassed: Boolean;
  RuntimeRestart: Boolean;
  RuntimeDownloadPage: TDownloadWizardPage;

function DefaultDirectory(Param: String): String;
begin
#ifdef TESTBUILD
  Result := ExpandConstant('{src}\installer-test-default');
#else
  Result := ExpandConstant('{localappdata}\Programs\Dictator');
  if FileExists(ExpandConstant('{localappdata}\Diktatoro\app\launcher.py')) then
    Result := ExpandConstant('{localappdata}\Diktatoro\app');
#endif
end;

function StartupCheckPassed: Boolean;
begin
  Result := CheckPassed;
end;

procedure InitializeWizard;
var Page: TOutputMsgWizardPage;
begin
  CheckPassed := True;
  RuntimeDownloadPage := CreateDownloadPage('Runtime', 'Intel / Microsoft', nil);
  Page := CreateOutputMsgPage(wpWelcome, CustomMessage('Intro'), 'Dictatoro 0.3', CustomMessage('Details'));
end;

function RuntimeInstalled: Boolean;
var Major, Minor, Build, Installed: Cardinal;
begin
  Result := RegQueryDWordValue(HKLM64, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64', 'Installed', Installed)
    and (Installed = 1)
    and RegQueryDWordValue(HKLM64, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64', 'Major', Major)
    and RegQueryDWordValue(HKLM64, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64', 'Minor', Minor)
    and RegQueryDWordValue(HKLM64, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64', 'Bld', Build)
    and ((Major > 14) or ((Major = 14) and ((Minor > 51) or ((Minor = 51) and (Build >= 36247)))));
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var Code: Integer;
begin
  Result := '';
#ifndef TESTBUILD
  if not IntelInstalled then begin
    if WizardSilent then begin
      Result := CustomMessage('IntelError');
      Exit;
    end;
    RuntimeDownloadPage.Clear;
    RuntimeDownloadPage.Add(
      'https://registrationcenter-download.intel.com/akdlm/IRC_NAS/47a201d7-d4cd-4079-a2d8-0e66b860aaaa/w_dpcpp_cpp_runtime_p_2025.2.1.1001.exe',
      'IntelRuntime.exe', 'ebec8698a742d5a17e628c685c31c0a121643517235d07ae5d47aba916db493b');
    RuntimeDownloadPage.Show;
    try
      try
        RuntimeDownloadPage.Download;
      except
        Result := CustomMessage('IntelError') + GetExceptionMessage;
        Exit;
      end;
    finally
      RuntimeDownloadPage.Hide;
    end;
    { Normal vendor UI: never silently accept Intel's license. }
    if not ShellExec('runas', ExpandConstant('{tmp}\IntelRuntime.exe'), '', '', SW_SHOWNORMAL, ewWaitUntilTerminated, Code) then begin
      Result := CustomMessage('IntelError') + IntToStr(Code);
      Exit;
    end;
    if (Code <> 0) and (Code <> 3010) and (Code <> 1641) then begin
      Result := CustomMessage('IntelError') + IntToStr(Code);
      Exit;
    end;
    RuntimeRestart := (Code = 3010) or (Code = 1641);
    if not IntelInstalled then begin
      Result := CustomMessage('IntelError');
      Exit;
    end;
  end;
  if not RuntimeInstalled then begin
    RuntimeDownloadPage.Clear;
    RuntimeDownloadPage.Add(
      'https://download.visualstudio.microsoft.com/download/pr/ebdab8e5-1d7b-4d9f-a11b-cbb1720c3b12/843068991DAAA1F73AD9F6239BCE4D0F6A07A51F18C37EA2A867E9BECA71295C/VC_redist.x64.exe',
      'VC_redist.x64.exe', '843068991daaa1f73ad9f6239bce4d0f6a07a51f18c37ea2a867e9beca71295c');
    RuntimeDownloadPage.Show;
    try
      try
        RuntimeDownloadPage.Download;
      except
        Result := CustomMessage('VCError') + GetExceptionMessage;
        Exit;
      end;
    finally
      RuntimeDownloadPage.Hide;
    end;
    { Microsoft displays its own license; Dictatoro does not accept it silently. }
    if not ShellExec('runas', ExpandConstant('{tmp}\VC_redist.x64.exe'), '/install /norestart', '', SW_SHOWNORMAL, ewWaitUntilTerminated, Code) then
      Result := CustomMessage('VCError') + IntToStr(Code)
    else if (Code <> 0) and (Code <> 3010) and (Code <> 1638) then
      Result := CustomMessage('VCError') + IntToStr(Code)
    else begin
      RuntimeRestart := RuntimeRestart or (Code = 3010);
      if not RuntimeInstalled then Result := CustomMessage('VCError') + IntToStr(Code);
    end;
  end;
#endif
end;

function NeedRestart: Boolean;
begin
  Result := RuntimeRestart;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var Code: Integer;
begin
  if CurStep = ssPostInstall then begin
#ifndef TESTBUILD
    if not WizardIsTaskSelected('startup') then
      RegDeleteValue(HKCU, 'Software\Microsoft\Windows\CurrentVersion\Run', '{#RunName}');
#endif
#ifndef TESTBUILD
    CheckPassed := Exec(ExpandConstant('{app}\Dictator.exe'), '--self-test', ExpandConstant('{app}'), SW_HIDE, ewWaitUntilTerminated, Code) and (Code = 0);
#endif
    if not CheckPassed then
      MsgBox(CustomMessage('CheckError'), mbError, MB_OK);
  end;
end;

function GetCustomSetupExitCode: Integer;
begin
  if CheckPassed then Result := 0 else Result := 10;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var DataPath: String;
begin
  if CurUninstallStep = usPostUninstall then begin
#ifndef TESTBUILD
    { Always remove startup, including when it was enabled later in the app. }
    RegDeleteValue(HKCU, 'Software\Microsoft\Windows\CurrentVersion\Run', '{#RunName}');
    if not UninstallSilent then
      if MsgBox(CustomMessage('RemoveData'), mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES then begin
        DataPath := ExpandConstant('{localappdata}\Diktatoro');
        { Only named application data; never remove an arbitrary installation directory. }
        DelTree(DataPath + '\models', True, True, True);
        DeleteFile(DataPath + '\settings.json');
        DeleteFile(DataPath + '\settings.tmp');
        DeleteFile(DataPath + '\app.log');
        DeleteFile(DataPath + '\startup-error.log');
        RemoveDir(DataPath);
      end;
#endif
  end;
end;

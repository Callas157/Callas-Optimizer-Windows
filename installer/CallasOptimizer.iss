; Callas Optimizer Setup Windows 11 x64
#define MyAppName "Callas Optimizer"
#define MyAppExe "Callas_Optimizer_Windows_x64.exe"
#define MyAppVersion GetEnv("CALLAS_VERSION")
#if MyAppVersion == ""
  #error CALLAS_VERSION nao definida
#endif
[Setup]
AppId={{33D8076A-342F-4AF7-8D18-1885BF08FC04}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=CallasTeck
AppPublisherURL=https://github.com/Callas157/Callas-Optimizer-Windows
AppUpdatesURL=https://github.com/Callas157/Callas-Optimizer-Windows/releases/latest
DefaultDirName={autopf}\Callas Optimizer
DefaultGroupName=Callas Optimizer
DisableProgramGroupPage=yes
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
SetupIconFile=..\assets\icons\callas.ico
UninstallDisplayIcon={app}\{#MyAppExe}
OutputDir=..\dist
OutputBaseFilename=Callas_Optimizer_Setup_x64
Compression=lzma2/max
SolidCompression=yes
CloseApplications=yes
RestartApplications=no
SetupLogging=yes
[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
[Tasks]
Name: "desktopicon"; Description: "Criar atalho na area de trabalho"; GroupDescription: "Atalhos:"; Flags: unchecked
[Files]
Source: "..\dist\{#MyAppExe}"; DestDir: "{app}"; Flags: ignoreversion
Source: "installed.marker"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{autoprograms}\Callas Optimizer"; Filename: "{app}\{#MyAppExe}"
Name: "{autodesktop}\Callas Optimizer"; Filename: "{app}\{#MyAppExe}"; Tasks: desktopicon
[Registry]
Root: HKLM; Subkey: "Software\CallasTeck\CallasOptimizer"; ValueType: string; ValueName: "InstallDir"; ValueData: "{app}"; Flags: uninsdeletekey
[Run]
Filename: "{app}\{#MyAppExe}"; Description: "Iniciar Callas Optimizer"; Flags: nowait postinstall skipifsilent

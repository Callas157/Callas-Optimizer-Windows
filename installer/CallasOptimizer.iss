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
VersionInfoDescription=Callas Optimizer
VersionInfoProductName=Callas Optimizer
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
UninstallDisplayIcon={app}\CallasOptimizer.ico
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
Source: "..\dist\Callas_Optimizer_Windows_x64\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\assets\icons\callas.ico"; DestDir: "{app}"; DestName: "CallasOptimizer.ico"; Flags: ignoreversion
Source: "installed.marker"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{autoprograms}\Callas Optimizer"; Filename: "{app}\{#MyAppExe}"; WorkingDir: "{app}"; IconFilename: "{app}\CallasOptimizer.ico"; AppUserModelID: "CallasTeck.CallasOptimizer.Windows"
Name: "{autodesktop}\Callas Optimizer"; Filename: "{app}\{#MyAppExe}"; WorkingDir: "{app}"; IconFilename: "{app}\CallasOptimizer.ico"; AppUserModelID: "CallasTeck.CallasOptimizer.Windows"; Tasks: desktopicon
[Registry]
Root: HKLM; Subkey: "Software\CallasTeck\CallasOptimizer"; ValueType: string; ValueName: "InstallDir"; ValueData: "{app}"; Flags: uninsdeletekey
[Run]
Filename: "{app}\{#MyAppExe}"; Description: "Iniciar Callas Optimizer"; Flags: nowait postinstall skipifsilent; Check: not IsCallasUpdate

[Code]
var
  RaisedUpdateWizard: Boolean;

function SetWindowPos(Window, InsertAfter: HWND; X, Y, Width, Height: Integer; Flags: Cardinal): Boolean;
  external 'SetWindowPos@user32.dll stdcall';
function SetForegroundWindow(Window: HWND): Boolean;
  external 'SetForegroundWindow@user32.dll stdcall';

function IsCallasUpdate: Boolean;
var
  I: Integer;
begin
  Result := False;
  for I := 1 to ParamCount do
    if CompareText(ParamStr(I), '/CALLASUPDATE') = 0 then
      Result := True;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if not IsCallasUpdate then
    Exit;
  if not RaisedUpdateWizard then
  begin
    RaisedUpdateWizard := True;
    SetWindowPos(WizardForm.Handle, HWND(-1), 0, 0, 0, 0, $0003);
    SetForegroundWindow(WizardForm.Handle);
  end
  else
    SetWindowPos(WizardForm.Handle, HWND(-2), 0, 0, 0, 0, $0013);
end;

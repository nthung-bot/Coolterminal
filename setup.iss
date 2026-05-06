; CoolTerminal - Inno Setup Script
; Requires: dist\coolterm.exe and dist\terconfig.exe (built via build.bat)
; Inno Setup 6: https://jrsoftware.org/isdl.php

[Setup]
AppName=CoolTerminal
AppVersion=1.0.0
AppPublisher=NguyenTanHung
AppPublisherURL=https://github.com/NguyenTanHung/CoolTerminal
AppSupportURL=https://github.com/NguyenTanHung/CoolTerminal/issues
AppUpdatesURL=https://github.com/NguyenTanHung/CoolTerminal/releases
DefaultDirName={autopf}\CoolTerminal
DefaultGroupName=CoolTerminal
AllowNoIcons=yes
OutputDir=Output
OutputBaseFilename=CoolTerminal-Installer
SetupIconFile=assets\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequiredOverridesAllowed=dialog
MinVersion=10.0
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "addtopath";      Description: "Add to PATH (recommended)";         GroupDescription: "Shell integration:"; Flags: checked
Name: "powershellhook"; Description: "Auto-display in PowerShell/Windows Terminal"; GroupDescription: "Shell integration:"; Flags: checked
Name: "cmdhook";        Description: "Auto-display in CMD";                GroupDescription: "Shell integration:"; Flags: checked

[Files]
Source: "dist\coolterm.exe";  DestDir: "{app}"; Flags: ignoreversion
Source: "dist\terconfig.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\CoolTerminal";  Filename: "{app}\coolterm.exe"
Name: "{group}\terconfig";     Filename: "{app}\terconfig.exe"
Name: "{group}\Uninstall";     Filename: "{uninstallexe}"

[Registry]
; Add to PATH
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; \
  ValueData: "{olddata};{app}"; \
  Check: NeedsAddPath(ExpandConstant('{app}')); \
  Tasks: addtopath

; CMD AutoRun
Root: HKCU; Subkey: "Software\Microsoft\Command Processor"; \
  ValueType: string; ValueName: "AutoRun"; \
  ValueData: """{app}\coolterm.exe"""; \
  Tasks: cmdhook

[Code]
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OrigPath) then
  begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
end;

procedure AddPowerShellProfile(AppDir: string);
var
  ProfilePath, Marker, Entry, Content: string;
begin
  ProfilePath := ExpandConstant('{userdocs}') + '\PowerShell\Microsoft.PowerShell_profile.ps1';
  Marker := '# CoolTerminal-autorun';
  Entry  := #13#10 + Marker + #13#10 +
            'if (Test-Path "' + AppDir + '\coolterm.exe") { & "' + AppDir + '\coolterm.exe" }' + #13#10;

  if FileExists(ProfilePath) then
  begin
    LoadStringFromFile(ProfilePath, Content);
    if Pos(Marker, Content) > 0 then exit;
  end
  else
    ForceDirectories(ExtractFileDir(ProfilePath));

  SaveStringToFile(ProfilePath, Entry, True);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    if IsTaskSelected('powershellhook') then
      AddPowerShellProfile(ExpandConstant('{app}'));
  end;
end;

[Run]
Filename: "cmd.exe"; \
  Parameters: "/k ""{app}\coolterm.exe"" && echo. && echo Type terconfig to configure."; \
  Description: "Open CMD and preview CoolTerminal"; \
  Flags: nowait postinstall skipifsilent

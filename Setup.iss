[Setup]
AppName=MergeApp
AppVersion=1.2.0
AppPublisher=JCM Contabilidade
DefaultDirName={autopf}\MergeApp
DefaultGroupName=MergeApp
OutputDir=.
OutputBaseFilename=Instalador_MergeApp
SetupIconFile=icone.ico
Compression=lzma/ultra
SolidCompression=yes
UninstallDisplayIcon={app}\MergeApp.exe

[Files]
Source: "dist\launcher.exe"; DestDir: "{app}"; DestName: "MergeApp.exe"; Flags: ignoreversion
Source: "icone.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\MergeApp"; Filename: "{app}\MergeApp.exe"; IconFilename: "{app}\icone.ico"
Name: "{commondesktop}\MergeApp"; Filename: "{app}\MergeApp.exe"; IconFilename: "{app}\icone.ico"; WorkingDir: "{app}"

[Registry]
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\MergeApp"; ValueType: string; ValueName: ""; ValueData: "Abrir com MergeApp"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\MergeApp"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\MergeApp.exe"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\MergeApp\command"; ValueType: string; ValueName: ""; ValueData: """{app}\MergeApp.exe"" ""%1"" %*"; Flags: uninsdeletevalue

[Run]
Filename: "{app}\MergeApp.exe"; Description: "Iniciar MergeApp agora"; Flags: nowait postinstall skipifsilent

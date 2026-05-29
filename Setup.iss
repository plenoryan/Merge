[Setup]
AppName=Mesclar PDFs
AppVersion=1.0
DefaultDirName={autopf}\Mesclar PDFs
DefaultGroupName=Mesclar PDFs
OutputDir=.
OutputBaseFilename=Instalador_MesclarPDFs
SetupIconFile=icone.ico
Compression=lzma/ultra
SolidCompression=no

[Files]
Source: "dist\merge\*"; DestDir: "{app}\merge"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\launcher\*"; DestDir: "{app}\launcher"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\separar\*"; DestDir: "{app}\separar"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "icone.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Mesclar PDFs"; Filename: "{app}\launcher\launcher.exe"; IconFilename: "{app}\icone.ico"
Name: "{commondesktop}\Mesclar PDFs"; Filename: "{app}\merge\merge.exe"; IconFilename: "{app}\icone.ico"; WorkingDir: "{app}"

[Registry]
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\Mesclar"; ValueType: string; ValueName: "MultiSelectModel"; ValueData: "Player"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\Mesclar\command"; ValueType: string; ValueName: ""; ValueData: """{app}\launcher\launcher.exe"" ""%1"" %*"; Flags: uninsdeletevalue

Root: HKCR; Subkey: "*\shell\Mesclar"; ValueType: string; ValueName: "MultiSelectModel"; ValueData: "Player"; Flags: uninsdeletekey
Root: HKCR; Subkey: "*\shell\Mesclar\command"; ValueType: string; ValueName: ""; ValueData: """{app}\launcher\launcher.exe"" ""%1"" %*"; Flags: uninsdeletevalue

Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\Separar"; ValueType: string; ValueName: "MultiSelectModel"; ValueData: "Player"; Flags: uninsdeletekey
Root: HKCR; Subkey: "SystemFileAssociations\.pdf\shell\Separar\command"; ValueType: string; ValueName: ""; ValueData: """{app}\separar\separar.exe"" ""%1"" %*"; Flags: uninsdeletevalue

Root: HKCR; Subkey: "*\shell\Separar"; ValueType: string; ValueName: "MultiSelectModel"; ValueData: "Player"; Flags: uninsdeletekey
Root: HKCR; Subkey: "*\shell\Separar\command"; ValueType: string; ValueName: ""; ValueData: """{app}\separar\separar.exe"" ""%1"" %*"; Flags: uninsdeletevalue

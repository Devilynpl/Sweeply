; Script generated programmatically by Sweeply Builder
[Setup]
AppId={{3B2C6D1F-7A9B-4D1C-8E2F-0C4B5D6E7F8A}}
AppName=Sweeply Desktop Cleaner
AppVersion=1.0b
AppPublisher=VirtuArch
AppPublisherURL=https://github.com/morbidnoizl/desktop_cleaner
AppSupportURL=https://github.com/morbidnoizl/desktop_cleaner
AppUpdatesURL=https://github.com/morbidnoizl/desktop_cleaner
DefaultDirName={autopf}\Sweeply
DefaultGroupName=Sweeply
DisableProgramGroupPage=yes
OutputDir=releases
OutputBaseFilename=Sweeply_Setup_x64
SetupIconFile=sweeply_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Files]
Source: "releases\DesktopCleanerHUD_x64.exe"; DestDir: "{app}"; DestName: "Sweeply.exe"; Flags: ignoreversion

[Icons]
Name: "{group}\Sweeply"; Filename: "{app}\Sweeply.exe"
Name: "{group}\Uninstall Sweeply"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Sweeply"; Filename: "{app}\Sweeply.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Sweeply.exe"; Description: "{{cm:LaunchProgram,Sweeply}}"; Flags: nowait postinstall skipifsilent

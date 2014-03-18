; Basic variables
!define PRODUCT_NAME "Mandriva Pulse Pull Client"
!define PRODUCT_VERSION "1.0.1"
!define PRODUCT_PUBLISHER "Mandriva S.A."
!define PRODUCT_WEB_SITE "http://www.mandriva.com"
!define PRODUCT_DIR_REGKEY "Software\Mandriva\Pulse-Pull-Client"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; Third-party plugins
!addPluginDir ".\plugins"

; MUI
!include "MUI.nsh"

; Lib to use if, else...
!include "LogicLib.nsh"
; Provides ${RunningX64} if statement
!include "x64.nsh"

; Use to get command line parameters (silent)
!include "FileFunc.nsh"
!insertmacro GetParameters
!insertmacro GetOptions

; Function to detect current windows version
!include "WinVer.nsh"

; A great function to compare versions
!include ".\libs\VersionCompare.nsh"
; "sed" macro
!include ".\libs\StrRep.nsh"
!include ".\libs\ReplaceInFile.nsh"
; Deal with custom options page
!include "libs\InstallOptionsMacro.nsh"

; A global variable containing version of the currently installed agent
Var /GLOBAL PREVIOUSVERSION

; Another containing path of the previously installed agent
Var /GLOBAL PREVIOUSINSTDIR

; Pulse DLP address
Var /GLOBAL DLP_SERVER
Var /GLOBAL DLP_PORT
Var /GLOBAL DLP_KEY

; Default values for DLP
!define DEFAULT_DLP_SERVER "dlp.domain.com"
!define DEFAULT_DLP_PORT "80"
!define DEFAULT_DLP_KEY "secret"

; Service name (from the Windows view)
!define WINSVCNAME "pulse_pull_client"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON ".\artwork\install.ico"
!define MUI_UNICON ".\artwork\uninstall.ico"
!define MUI_WELCOMEPAGE_TITLE_3LINES
!define MUI_HEADERIMAGE
!define MUI_WELCOMEFINISHPAGE_BITMAP ".\artwork\wizard.bmp"
!define MUI_HEADERIMAGE_RIGHT
!define MUI_HEADERIMAGE_BITMAP ".\artwork\header.bmp"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; Custom page with DLP address
Page custom CustomOptions
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES
; Language files
!insertmacro MUI_LANGUAGE "English"

Name "${PRODUCT_NAME} (${PRODUCT_VERSION})"
OutFile "pulse2-pull-client-${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES\Mandriva\Pulse-Pull-Client"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

; Custom options page
ReserveFile "customoptions.ini"
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS

; Custom options page pre-setting
Function CustomOptions
  !insertmacro MUI_HEADER_TEXT "Configure Pulse DownLoad Provider URL" "This URL should be pre-filled correctly"
  !insertmacro INSTALLOPTIONS_INITDIALOG "customoptions.ini"
  ; Try to pre-fill fileds with command line parameters
  ${IfNot} $DLP_SERVER == ""
    !insertmacro CHANGETEXTFIELD "customoptions.ini" "Field 3" $DLP_SERVER
  ${EndIf}
  ${IfNot} $DLP_PORT == ""
    !insertmacro CHANGETEXTFIELD "customoptions.ini" "Field 5" $DLP_PORT
  ${EndIf}
  ${IfNot} $DLP_KEY == ""
    !insertmacro CHANGETEXTFIELD "customoptions.ini" "Field 7" $DLP_KEY
  ${EndIf}
  !insertmacro INSTALLOPTIONS_SHOW
FunctionEnd

; First function run
Function .onInit
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; CHECK IF IT'S A NT-BASED OS ;
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; Won't work on old OS
  ${IfNot} ${AtLeastWinXp}
    MessageBox MB_OK|MB_ICONEXCLAMATION "You cannot install $(^Name) unless you're running Windows XP or newer."
    Abort
  ${EndIf}i

  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; GET PREVIOUS AGENT VERSION AND PATH ;
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; ReadRegStr will set the Errors flag if the key doesn't exist
  ClearErrors
  ReadRegStr $0 HKLM "Software\Mandriva\Pulse-Pull-Client" "CurrentVersion"
  ${If} ${Errors}
    ; No previously installed agent
    StrCpy $PREVIOUSVERSION "1.0"
  ${Else}
    ; Use $0 which contains the right version
    StrCpy $PREVIOUSVERSION $0
  ${EndIf}
  ; ReadRegStr will set the Errors flag if the key doesn't exist
  ClearErrors
  ReadRegStr $0 HKLM "Software\Mandriva\OpenSSH" "InstallPath"
  ${If} ${Errors}
    ; The key doesn't exists, it means that previous version was older
    ; than 1.2.X
    ; Use default INSTDIR
    StrCpy $PREVIOUSINSTDIR $INSTDIR
  ${Else}
    ; Use $0 which contains the previous installation path
    StrCpy $PREVIOUSINSTDIR $0
  ${EndIf}

  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; CHECK IF OPENSSH IS INSTALLED ;
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; ReadRegStr will set the Errors flag if the key doesn't exist
  ClearErrors
  ReadRegStr $0 HKLM "Software\Mandriva\OpenSSH" "CurrentVersion"
  ${If} ${Errors}
    MessageBox MB_OK|MB_ICONEXCLAMATION "You cannot install $(^Name) without having Mandriva Pulse2 Secure Agent (>= 2.1.0) already installed."
    Abort
  ${Else}
    ; SSH < 2.1.0
    ${VersionCompare} $0 "2.1.0" $R0
    ${If} $R0 == 2
      MessageBox MB_OK|MB_ICONEXCLAMATION "You cannot install $(^Name) with Mandriva Pulse2 Secure Agent < 2.1.0. Please update it first."
      Abort
    ${EndIf}
  ${EndIf}

  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; Required for custom options page ;
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  !insertmacro MUI_INSTALLOPTIONS_EXTRACT "customoptions.ini"

  ;;;;;;;;;;;;;;;;;;;;;;;
  ; Command line params ;
  ;;;;;;;;;;;;;;;;;;;;;;;
  ${GetParameters} $R0

  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; Handle /DLP_SERVER option ;
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ${GetOptions} $R0 "/DLP_SERVER=" $0
  StrCpy $DLP_SERVER $0
  ${If} $DLP_SERVER == ""
    StrCpy $DLP_SERVER ${DEFAULT_DLP_SERVER}
  ${EndIf}
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; Handle /DLP_PORT option ;
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ${GetOptions} $R0 "/DLP_PORT=" $0
  StrCpy $DLP_PORT $0
  ${If} $DLP_PORT == ""
    StrCpy $DLP_PORT ${DEFAULT_DLP_PORT}
  ${EndIf}
  ;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; Handle /DLP_KEY option ;
  ;;;;;;;;;;;;;;;;;;;;;;;;;;
  ${GetOptions} $R0 "/DLP_KEY=" $0
  StrCpy $DLP_KEY $0
  ${If} $DLP_KEY == ""
    StrCpy $DLP_KEY ${DEFAULT_DLP_KEY}
  ${EndIf}
  
  ;;;;;;;;;;;;;;;;;;;;
  ; Handle /S option ;
  ;;;;;;;;;;;;;;;;;;;;
  ClearErrors
  ${GetOptions} $R0 /S $0
  ${If} ${Errors} ; "Silent mode" flag not set
    SetSilent normal
  ${Else} ; "Silent mode" flag set
    SetSilent silent
  ${EndIf}

FunctionEnd

; Pre-install clean
Section "Clean" Clean
  SectionIn RO
  DetailPrint "* 1. Pre-installation step"
  
  Push '${WINSVCNAME}'
  Services::IsServiceInstalled
  Pop $0
  ; $0 now contains either 'Yes', 'No' or an error description
  ${If} $0 == 'Yes'
    ; This will stop and remove the service if it is running.
    DetailPrint "Previously installed Pulse Pull Client service found. Trying to stop and remove it."
    push '${WINSVCNAME}'
    push 'Stop'
    Services::SendServiceCommand
    push '${WINSVCNAME}'
    push 'Delete'
    Services::SendServiceCommand
    Pop $0
    ${If} $0 != 'Ok'
      MessageBox MB_OK|MB_ICONSTOP 'The installer found a previously installed Pulse Pull Client service, but was unable to remove it.$\r$\n$\r$\nPlease stop it and manually remove it. Then try installing again.'
      Abort
    ${EndIf}
    ; Wait one second for the service to be really stopped
    Sleep 1000
  ${EndIf}
SectionEnd

; Main install
Section "Core" Core
  SectionIn RO
  DetailPrint ""
  DetailPrint "* 2. Main installation step"

  SetOutPath "$INSTDIR"
  SetOverwrite on
  File bin\_socket.pyd
  File bin\python27.dll
  File bin\win32evtlog.pyd
  File bin\pyexpat.pyd
  File bin\unicodedata.pyd
  File bin\win32api.pyd
  File bin\pywintypes27.dll
  File bin\library.zip
  File bin\_hashlib.pyd
  File bin\_ssl.pyd
  File bin\bz2.pyd
  File bin\win32pipe.pyd
  File bin\select.pyd
  File bin\cx_Logging.pyd
  File bin\service.exe
  File bin\Microsoft.VC90.CRT.manifest
  File bin\msvcm90.dll
  File bin\msvcp90.dll
  File bin\MSVCR90.dll

  ;;;;;;;;;;;;;
  ; Conf file ;
  ;;;;;;;;;;;;;
  
  SetOutPath "$INSTDIR\conf"
  SetOverwrite on
  File bin\conf\pull_client.conf

  ; Read from custom page
  ${IfNot} ${Silent}
    ReadINIStr $0 "$PLUGINSDIR\customoptions.ini" "Field 3" "State"
    ${If} $0 == ""
      MessageBox MB_OK|MB_ICONEXCLAMATION "Pulse DownLoad Provider address is empty! $\n\
Please fill the field with the right DNS name or IP address."
      Abort
    ${EndIf}
    StrCpy $DLP_SERVER $0
    ReadINIStr $1 "$PLUGINSDIR\customoptions.ini" "Field 5" "State"
    ${If} $1 == ""
      MessageBox MB_OK|MB_ICONEXCLAMATION "Pulse DownLoad Provider port is empty! $\n\
Please fill the field with the right port."
      Abort
    ${EndIf}
    StrCpy $DLP_PORT $1
    ReadINIStr $2 "$PLUGINSDIR\customoptions.ini" "Field 7" "State"
    ${If} $2 == ""
      MessageBox MB_OK|MB_ICONEXCLAMATION "Pulse DownLoad Provider key is empty! $\n\
Please fill the field with the right security key."
      Abort
    ${EndIf}
    StrCpy $DLP_KEY $2
  ${EndIF}

  ; Fix conf file
  DetailPrint "Using $DLP_SERVER:$DLP_PORT as DLP server."
  DetailPrint "Using $DLP_KEY as DLP security key."
  !insertmacro _ReplaceInFile "$INSTDIR\conf\pull_client.conf" "@@DLP_SERVER@@" $DLP_SERVER
  !insertmacro _ReplaceInFile "$INSTDIR\conf\pull_client.conf" "@@DLP_PORT@@" $DLP_PORT
  !insertmacro _ReplaceInFile "$INSTDIR\conf\pull_client.conf" "@@DLP_KEY@@" $DLP_KEY
  !insertmacro _ReplaceInFile "$INSTDIR\conf\pull_client.conf" "@@LOG_PATH@@" $INSTDIR\pull_client_log.txt

  ;;;;;;;;;;;;;;;;;;;;
  ; Register service ;
  ;;;;;;;;;;;;;;;;;;;;
  DetailPrint "Running $INSTDIR\service.exe --install pulse_pull_client"
  nsExec::ExecToLog "$INSTDIR\service.exe --install pulse_pull_client"
  Pop $0
  ; May return "error" in $0 if something goes wrong
  ${If} $0 == 'error'
    MessageBox MB_OK|MB_ICONEXCLAMATION 'Something went wrong when trying to register Pulse Pull Client service.$\r$\n$\r$\nYou may try to run the following command manually to have more information:$\r$\n  "$INSTDIR\pulse_pull_client.exe" --install'
    Abort
  ${EndIf}
  ; Well is it REALLY installed ? Let's figure out.
  Push '${WINSVCNAME}'
  Services::IsServiceInstalled
  Pop $0
  ; $0 now contains either 'Yes', 'No' or an error description
  ${If} $0 != 'Yes'
    MessageBox MB_OK|MB_ICONEXCLAMATION 'Something went wrong when trying to register Pulse Pull Client service.$\r$\n$\r$\nYou may try to run the following command manually to have more information:$\r$\n  "$INSTDIR\pulse_pull_client.exe" --install'
    Abort
  ${EndIf}

SectionEnd

; Post-install (create uninst.exe and register app in unistall registry database)
Section -Post
  DetailPrint ""
  DetailPrint "* 3. Post-installation step"
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  ; Write a CurrentVersion variable
  ; This must be done after installation, otherwise it would overwrite previous version number
  WriteRegStr HKLM "Software\Mandriva\Pulse-Pull-Client" "CurrentVersion" "${PRODUCT_VERSION}"
  WriteRegStr HKLM "Software\Mandriva\Pulse-Pull-Client" "InstallPath" "$INSTDIR"
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${Clean} "Pre-installation step"
!insertmacro MUI_DESCRIPTION_TEXT ${Core} "Mandriva Pulse Pull Client"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Postuninstall function
Function un.onUninstSuccess
  ${IfNot} ${Silent}
    HideWindow
    MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
  ${EndIf}
FunctionEnd

; First function run at uninstall time (ask confirm)
Function un.onInit
  ${IfNot} ${Silent}
    MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
    Abort
  ${EndIf}
FunctionEnd

; What do to when unstalling
Section Uninstall

  ; Stop/Delete service
  Push '${WINSVCNAME}'
  Services::IsServiceInstalled
  Pop $0
  ; $0 now contains either 'Yes', 'No' or an error description
  ${If} $0 == 'Yes'
    ; This will stop and remove the service if it is running.
    DetailPrint "Previously installed Pulse Pull Client service found. Trying to stop and remove it."
    push '${WINSVCNAME}'
    push 'Stop'
    Services::SendServiceCommand
    push '${WINSVCNAME}'
    push 'Delete'
    Services::SendServiceCommand
    Pop $0
    ${If} $0 != 'Ok'
      MessageBox MB_OK|MB_ICONSTOP 'The installer found a previously installed Pulse Pull Client service, but was unable to remove it.$\r$\n$\r$\nPlease stop it and manually remove it. Then try installing again.'
      Abort
    ${EndIf}
    ; Wait one second for the service to be really stopped
    Sleep 1000
  ${EndIf}

  ; Drop uninstaller and files
  Delete "$INSTDIR\uninst.exe"
  RMDir /r "$INSTDIR"
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"

  ; Delete registry entries specific to the product
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"

  SetAutoClose true
SectionEnd

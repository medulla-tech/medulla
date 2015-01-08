; Basic variables
!define PRODUCT_NAME "Mandriva Pulse2 Agent"
!define PRODUCT_VERSION "0.0.1"
!define PRODUCT_PUBLISHER "Mandriva S.A."
!define PRODUCT_WEB_SITE "http://www.mandriva.com"
!define PRODUCT_DIR_REGKEY "Software\Mandriva\Pulse2Agent"
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

; Pulse PULSE2_CM address
Var /GLOBAL PULSE2_CM_SERVER
Var /GLOBAL PULSE2_CM_PORT

; Default values for PULSE2_CM
!define DEFAULT_PULSE2_CM_SERVER "pulse2.domain.com"
!define DEFAULT_PULSE2_CM_PORT "8443"

; Service name (from the Windows view)
!define WINSVCNAME "pulse2-agent"

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
; Custom page with PULSE2_CM address
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
OutFile "pulse2-agent-${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES\Mandriva\Pulse2-Agent"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

; Custom options page
ReserveFile "customoptions.ini"
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS

; Custom options page pre-setting
Function CustomOptions
  !insertmacro MUI_HEADER_TEXT "Configure Pulse Connection Manager host" "This should be pre-filled correctly"
  !insertmacro INSTALLOPTIONS_INITDIALOG "customoptions.ini"
  ; Try to pre-fill fileds with command line parameters
  ${IfNot} $PULSE2_CM_SERVER == ""
    !insertmacro CHANGETEXTFIELD "customoptions.ini" "Field 3" $PULSE2_CM_SERVER
  ${EndIf}
  ${IfNot} $PULSE2_CM_PORT == ""
    !insertmacro CHANGETEXTFIELD "customoptions.ini" "Field 5" $PULSE2_CM_PORT
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
  ReadRegStr $0 HKLM "Software\Mandriva\Pulse2Agent" "CurrentVersion"
  ${If} ${Errors}
    ; No previously installed agent
    StrCpy $PREVIOUSVERSION "0.1"
  ${Else}
    ; Use $0 which contains the right version
    StrCpy $PREVIOUSVERSION $0
  ${EndIf}
  ; ReadRegStr will set the Errors flag if the key doesn't exist
  ClearErrors
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; Required for custom options page ;
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  !insertmacro MUI_INSTALLOPTIONS_EXTRACT "customoptions.ini"

  ;;;;;;;;;;;;;;;;;;;;;;;
  ; Command line params ;
  ;;;;;;;;;;;;;;;;;;;;;;;
  ${GetParameters} $R0

  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; Handle /PULSE2_CM_SERVER option ;
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ${GetOptions} $R0 "/PULSE2_CM_SERVER=" $0
  StrCpy $PULSE2_CM_SERVER $0
  ${If} $PULSE2_CM_SERVER == ""
    StrCpy $PULSE2_CM_SERVER ${DEFAULT_PULSE2_CM_SERVER}
  ${EndIf}
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; Handle /PULSE2_CM_PORT option ;
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ${GetOptions} $R0 "/PULSE2_CM_PORT=" $0
  StrCpy $PULSE2_CM_PORT $0
  ${If} $PULSE2_CM_PORT == ""
    StrCpy $PULSE2_CM_PORT ${DEFAULT_PULSE2_CM_PORT}
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
    DetailPrint "Previously installed Pulse Agent service found. Trying to stop and remove it."
    push '${WINSVCNAME}'
    push 'Stop'
    Services::SendServiceCommand
    push '${WINSVCNAME}'
    push 'Delete'
    Services::SendServiceCommand
    Pop $0
    ${If} $0 != 'Ok'
      MessageBox MB_OK|MB_ICONSTOP 'The installer found a previously installed Pulse Agent service, but was unable to remove it.$\r$\n$\r$\nPlease stop it and manually remove it. Then try installing again.'
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
  File bin\MSVCR90.dll
  File bin\Microsoft.VC90.CRT.manifest
  File bin\_hashlib.pyd
  File bin\_socket.pyd
  File bin\_ssl.pyd
  File bin\bz2.pyd
  File bin\cx_Logging.pyd
  File bin\service.exe
  File bin\library.zip
  File bin\mfc90.dll
  File bin\msvcm90.dll
  File bin\msvcp90.dll
  File bin\pyexpat.pyd
  File bin\python27.dll
  File bin\pythoncom27.dll
  File bin\pywintypes27.dll
  File bin\select.pyd
  File bin\unicodedata.pyd
  File bin\win32api.pyd
  File bin\win32evtlog.pyd
  File bin\win32pipe.pyd
  File bin\win32ui.pyd
  

  ;;;;;;;;;;;;;
  ; Conf file ;
  ;;;;;;;;;;;;;
  
  SetOutPath "$INSTDIR"
  SetOverwrite on
  File bin\agent.ini

  ; Read from custom page
  ${IfNot} ${Silent}
    ReadINIStr $0 "$PLUGINSDIR\customoptions.ini" "Field 3" "State"
    ${If} $0 == ""
      MessageBox MB_OK|MB_ICONEXCLAMATION "Pulse2 Connection Manager address is empty! $\n\
Please fill the field with the right DNS name or IP address."
      Abort
    ${EndIf}
    StrCpy $PULSE2_CM_SERVER $0
    ReadINIStr $1 "$PLUGINSDIR\customoptions.ini" "Field 5" "State"
    ${If} $1 == ""
      MessageBox MB_OK|MB_ICONEXCLAMATION "Pulse2 Connection Manager port is empty! $\n\
Please fill the field with the right port."
      Abort
    ${EndIf}
    StrCpy $PULSE2_CM_PORT $1
    ReadINIStr $2 "$PLUGINSDIR\customoptions.ini" "Field 7" "State"
  ${EndIF}

  ; Fix conf file
  DetailPrint "Using $PULSE2_CM_SERVER:$PULSE2_CM_PORT as Connection Manager."
  !insertmacro _ReplaceInFile "$INSTDIR\agent.ini" "@@PULSE2_CM_SERVER@@" $PULSE2_CM_SERVER
  !insertmacro _ReplaceInFile "$INSTDIR\agent.ini" "@@PULSE2_CM_PORT@@" $PULSE2_CM_PORT
  !insertmacro _ReplaceInFile "$INSTDIR\agent.ini" "@@PULSE2_CM_LOG_PATH@@" $INSTDIR\pulse2-agent.log.txt

  ;;;;;;;;;;;;;;;;;;;;
  ; Register service ;
  ;;;;;;;;;;;;;;;;;;;;
  DetailPrint "Running $INSTDIR\service.exe --install pulse2-agent"
  nsExec::ExecToLog "$INSTDIR\service.exe --install pulse2-agent"
  Pop $0
  ; May return "error" in $0 if something goes wrong
  ${If} $0 == 'error'
    MessageBox MB_OK|MB_ICONEXCLAMATION '1:Something went wrong when trying to register Pulse2 Agent service.$\r$\n$\r$\nYou may try to run the following command manually to have more information:$\r$\n  "$INSTDIR\service.exe" --install'
    Abort
  ${EndIf}
  ; Well is it REALLY installed ? Let's figure out.
  Push '${WINSVCNAME}'
  Services::IsServiceInstalled
  Pop $0
  ; $0 now contains either 'Yes', 'No' or an error description
  ${If} $0 != 'Yes'
    MessageBox MB_OK|MB_ICONEXCLAMATION '2:Something went wrong when trying to register Pulse2 Agent service.$\r$\n$\r$\nYou may try to run the following command manually to have more information:$\r$\n  "$INSTDIR\service.exe" --install'
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
  WriteRegStr HKLM "Software\Mandriva\Pulse2-Agent" "CurrentVersion" "${PRODUCT_VERSION}"
  WriteRegStr HKLM "Software\Mandriva\Pulse2-Agent" "InstallPath" "$INSTDIR"
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${Clean} "Pre-installation step"
!insertmacro MUI_DESCRIPTION_TEXT ${Core} "Mandriva Pulse2 Agent"
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
    DetailPrint "Previously installed Pulse2 Agent service found. Trying to stop and remove it."
    push '${WINSVCNAME}'
    push 'Stop'
    Services::SendServiceCommand
    push '${WINSVCNAME}'
    push 'Delete'
    Services::SendServiceCommand
    Pop $0
    ${If} $0 != 'Ok'
      MessageBox MB_OK|MB_ICONSTOP 'The installer found a previously installed Pulse2 Agent service, but was unable to remove it.$\r$\n$\r$\nPlease stop it and manually remove it. Then try installing again.'
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

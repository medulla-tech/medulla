; Basic variables
!define PRODUCT_NAME "Mandriva Secure Agent [Windows Update plugin]"
!define PRODUCT_VERSION "1.0.0"
!define PRODUCT_PUBLISHER "Mandriva S.A."
!define PRODUCT_WEB_SITE "http://www.mandriva.com"
!define PRODUCT_DIR_REGKEY "Software\Mandriva\Windows-Update-Plugin"
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

; A global variable containing version of the currently installed agent
; Will contains 1.0 if no registry key exists, which means either pre-1.1.0
; is installed, or not agent at all installed.
Var /GLOBAL PREVIOUSVERSION

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
; Directory page (do not show)
;!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES
; Language files
!insertmacro MUI_LANGUAGE "English"

Name "${PRODUCT_NAME} (${PRODUCT_VERSION})"
OutFile "pulse2-secure-agent-windows-update-plugin-${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES\Mandriva\Windows-Update-Plugin"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

; First function run
Function .onInit
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; CHECK IF IT'S A NT-BASED OS ;
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; Won't work on old OS
  ${IfNot} ${AtLeastWinXp}
    MessageBox MB_OK|MB_ICONEXCLAMATION "You cannot install $(^Name) unless you're running Windows XP or newer."
    Abort
  ${EndIf}
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; GET PREVIOUS AGENT VERSION AND PATH ;
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; ReadRegStr will set the Errors flag if the key doesn't exist
  ClearErrors
  ReadRegStr $0 HKLM "Software\Mandriva\Windows-Update-Plugin" "CurrentVersion"
  ${If} ${Errors}
    ; No previously installed agent
    StrCpy $PREVIOUSVERSION "1.0"
  ${Else}
    ; Use $0 which contains the right version
    StrCpy $PREVIOUSVERSION $0
  ${EndIf}
  ; Try to figure out where OpenSSH is installed
  ; ReadRegStr will set the Errors flag if the key doesn't exist
  ClearErrors
  ReadRegStr $0 HKLM "Software\Mandriva\OpenSSH" "InstallPath"
  ${If} ${Errors}
    MessageBox MB_OK|MB_ICONEXCLAMATION "You cannot install $(^Name) without having Mandriva Pulse2 Secure Agent already installed."
    Abort
  ${Else}
    ; This is default instdir
    StrCpy $INSTDIR $0
  ${EndIf}
FunctionEnd

Section "Core" Core
  SectionIn RO

  SetOutPath "$INSTDIR\usr\share\pulse-update-manager"
  SetOverwrite on

  ; Files not depending on cygwin dlls
  File bin\python27.dll
  File bin\msvcm90.dll
  File bin\MSVCR90.dll
  File bin\mfc90.dll
  File bin\pythoncom27.dll
  File bin\unicodedata.pyd
  File bin\win32ui.pyd
  File bin\win32api.pyd
  File bin\pywintypes27.dll
  File bin\pulse-update-manager.exe
  File bin\library.zip
  File bin\msvcp90.dll
  File bin\bz2.pyd
  File bin\Microsoft.VC90.CRT.manifest
SectionEnd

; Postinstall (create uninst.exe and register app in unistall registry database)
Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  ; Write a CurrentVersion variable
  ; This must be done after installation, otherwise it would overwrite previous version number
  WriteRegStr HKLM "Software\Mandriva\Windows-Update-Plugin" "CurrentVersion" "${PRODUCT_VERSION}"
  WriteRegStr HKLM "Software\Mandriva\Windows-Update-Plugin" "InstallPath" "$INSTDIR"
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${Core} "Mandriva Secure Agent (Windows Update plugin)"
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
  ; Drop uninstaller and files
  Delete "$INSTDIR\uninst.exe"
  RMDir /r "$INSTDIR"
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"

  ; Delete registry entries specific to the product
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"

  SetAutoClose true
SectionEnd

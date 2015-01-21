; Stolen from http://nsis.sourceforge.net/Useful_InstallOptions_and_MUI_macros

; Activate a group of controls, depending on the state of one control
; 
; Usage:
; 
; eg. !insertmacro GROUPCONTROLS "${DIALOG1}" "${CHK_PROXYSETTINGS}" 
; "${LBL_IPADDRESS}|${TXT_IPADDRESS}|${LBL_PORT1}|${TXT_PORT1}|${CHK_ENCRYPTION}"
; FILE:          INI-file in $pluginsdir
; SOURCECONTROL: RadioButton, Checkbox
; CONTROLGROUP:  pipe delimited list of controls; ${BUTTON1}|${CHECKBOX}|${TEXTFIELD}
;
; Requires:
;
; !include "WordFunc.nsh"
; !insertmacro WordReplace
; !insertmacro WordFind
;
!macro GROUPCONTROLS FILE SOURCECONTROL CONTROLGROUP
  Push $R0 ;holds element
  Push $R1 ;counter
  Push $R2 ;state of the control
  Push $R3 ;flags of the control / hwnd of the control
 
  !insertmacro MUI_INSTALLOPTIONS_READ $R2 "${FILE}" "${SOURCECONTROL}" "State"
 
  StrCpy $R1 1
  ${Do}
    ClearErrors
    ${WordFind} "${CONTROLGROUP}" "|" "E+$R1" $R0
 
    ${If} ${Errors}
    ${OrIf} $R0 == ""
      ${ExitDo}
    ${EndIf}
 
    ; Put state change in flags of element as well
    !insertmacro MUI_INSTALLOPTIONS_READ $R3 "${FILE}" "$R0" "Flags"
    ${If} "$R2" == "1"
      ${WordReplace} $R3 "DISABLED" "" "+" $R3
       ${WordReplace} $R3 "||" "|" "+" $R3
      !insertmacro MUI_INSTALLOPTIONS_WRITE "${FILE}" "$R0" "Flags" $R3
    ${Else}
      !insertmacro MUI_INSTALLOPTIONS_WRITE "${FILE}" "$R0" "Flags" "$R3|DISABLED"
    ${EndIf}
 
    !insertmacro MUI_INSTALLOPTIONS_READ $R3 "${FILE}" "$R0" "HWND"
    EnableWindow $R3 $R2
 
    IntOp $R1 $R1 + 1
  ${Loop}
 
  Pop $R3
  Pop $R2
  Pop $R1
  Pop $R0
 
!macroend


;change text field and put value in ini file
; 
; Usage:
;
;  !insertmacro CHANGETEXTFIELD "${DIALOG1}" "${DRQ_NSISPATH}" $tmp
;
; FILE:    INI-file in $pluginsdir
; ELEMENT: name of the control
; VALUE:   value that should appear in control
;
!macro CHANGETEXTFIELD FILE ELEMENT VALUE
  Push $R0 ; holds value
  !insertmacro MUI_INSTALLOPTIONS_WRITE ${VALUE} "${FILE}" "${ELEMENT}" "State"
  !insertmacro MUI_INSTALLOPTIONS_READ $R0 "${FILE}" "${ELEMENT}" "HWND"
  SendMessage $R0 ${WM_SETTEXT} 0 "STR:${VALUE}"
  Pop $R0
!macroend


; checks a group of checkboxes and counts how many of them
; are activated.
;
; Usage:
;
; Create a langstring containing an error message
; eg. LangString TEXT_LIMITATIONSEXEEDED ${LANG_ENGLISH} "Choose either two or three colours!"
;
; eg. !insertmacro CHECKBOXCHECKER "${DIALOG1}" "${CHK_BLUE}|${CHK_RED}|${CHK_GREEN}|${CHK_BROWN}" 2 3
;
; FILE:          INI-file in $pluginsdir
; CONTROLGROUP:  pipe delimited list of controls; ${BUTTON1}|${CHECKBOX}|${TEXTFIELD}
; MIN/MAX:       at least ${MIN} and no more than ${MAX} controls must be in activated state
;
; Requires:
;
; !include "WordFunc.nsh"
; !insertmacro WordFind
;
!macro CHECKBOXCHECKER FILE CONTROLGROUP MIN MAX
 
  Push $R0 ;holds element
  Push $R1 ;counter
  Push $R2 ;count activated elements
  Push $R3 ;state of the control
 
  StrCpy $R1 1
  StrCpy $R2 0
  ${Do}
    ClearErrors
    ${WordFind} "${CONTROLGROUP}" "|" "E+$R1" $R0
 
    ${If} ${Errors}
    ${OrIf} $R0 == ""
      ${ExitDo}
    ${EndIf}
 
    ; Put state change in flags of element as well
    !insertmacro MUI_INSTALLOPTIONS_READ $R3 "${FILE}" "$R0" "State"
    ${If} "$R3" == "1"
      IntOp $R2 $R2 + 1
    ${EndIf}
 
    IntOp $R1 $R1 + 1
  ${Loop}
 
  ${If} $R2 < ${MIN}
  ${OrIf} $R2 > ${MAX}
    MessageBox MB_OK|MB_ICONSTOP "$(TEXT_LIMITATIONSEXCEEDED)"
    Abort
  ${EndIf}
 
  Pop $R3
  Pop $R2
  Pop $R1
  Pop $R0
 
!macroend

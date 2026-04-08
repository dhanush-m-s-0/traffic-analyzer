; Traffic Analyzer NSIS Installer Script
; Requires NSIS 3.x (https://nsis.sourceforge.io/)

!define APP_NAME      "Traffic Analyzer"
!define APP_VERSION   "1.0.0"
!define APP_EXE       "traffic-analyzer.exe"
!define PUBLISHER     "Traffic Analyzer Project"
!define URL           "https://github.com/dhanush-m-s-0/traffic-analyzer"
!define INSTALL_DIR   "$PROGRAMFILES64\${APP_NAME}"
!define REG_KEY       "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

; --- Metadata ---------------------------------------------------------
Name                "${APP_NAME} ${APP_VERSION}"
OutFile             "dist\traffic-analyzer-setup.exe"
InstallDir          "${INSTALL_DIR}"
InstallDirRegKey    HKLM "${REG_KEY}" "InstallLocation"
RequestExecutionLevel admin
SetCompressor       lzma

; --- MUI2 interface ---------------------------------------------------
!include "MUI2.nsh"
!define MUI_ABORTWARNING
!define MUI_ICON "traffic-analyzer.ico"
!define MUI_UNICON "traffic-analyzer.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.md"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

; --- Installation -----------------------------------------------------
Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  File "dist\${APP_EXE}"
  File /oname=README.md "README.md"
  File /oname=README_EXE.md "README_EXE.md"
  File /oname=.env.example ".env.example"

  ; Write uninstall registry keys
  WriteRegStr HKLM "${REG_KEY}" "DisplayName"      "${APP_NAME}"
  WriteRegStr HKLM "${REG_KEY}" "UninstallString"  "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "${REG_KEY}" "InstallLocation"  "$INSTDIR"
  WriteRegStr HKLM "${REG_KEY}" "Publisher"        "${PUBLISHER}"
  WriteRegStr HKLM "${REG_KEY}" "URLInfoAbout"     "${URL}"
  WriteRegStr HKLM "${REG_KEY}" "DisplayVersion"   "${APP_VERSION}"
  WriteRegDWORD HKLM "${REG_KEY}" "NoModify" 1
  WriteRegDWORD HKLM "${REG_KEY}" "NoRepair" 1

  ; Uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"

  ; Desktop shortcut
  CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0

  ; Start Menu shortcuts
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk"   "$INSTDIR\uninstall.exe"
SectionEnd

; --- Uninstaller -------------------------------------------------------
Section "Uninstall"
  Delete "$INSTDIR\${APP_EXE}"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\README_EXE.md"
  Delete "$INSTDIR\.env.example"
  Delete "$INSTDIR\uninstall.exe"
  RMDir  "$INSTDIR"

  Delete "$DESKTOP\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
  Delete "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk"
  RMDir  "$SMPROGRAMS\${APP_NAME}"

  DeleteRegKey HKLM "${REG_KEY}"
SectionEnd

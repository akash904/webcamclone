; WebCamClone Installer Script
; Created for WebCamClone application

!define APPNAME "Webcam Clone"
!define COMPANYNAME "Webcam Clone"
!define DESCRIPTION "A free, open-source software."
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/yourusername/webcamclone" ; "Support Information" link
!define UPDATEURL "https://github.com/yourusername/webcamclone" ; "Product Updates" link
!define ABOUTURL "https://github.com/yourusername/webcamclone" ; "Publisher" link
!define INSTALLSIZE 50000 ; Size in KB

RequestExecutionLevel admin ;Require admin rights on NT6+ (When UAC is turned on)

InstallDir "$PROGRAMFILES\${APPNAME}"

Name "${APPNAME}"
outFile "WebCamClone_Installer.exe"

!include LogicLib.nsh

; Just three pages - license agreement, install location, and installation
page license
page directory
Page instfiles

; License data
LicenseData "LICENSE"

; Installer sections
Section "install"
    ; Files for the install directory - to build the installer, these should be in the same directory as the install script
    setOutPath $INSTDIR
    ; Files added here should be removed by the uninstaller (see section "uninstall")
    file "dist\WebCamClone.exe"
    file "wc.ico"
    file "LICENSE"
    file "README.md"
    
    ; Install virtual camera files
    setOutPath "$INSTDIR\Install_virtual_cam"
    file "Install_virtual_cam\Install.bat"
    file "Install_virtual_cam\InstallCustomName.bat"
    file "Install_virtual_cam\InstallMultipleDevices.bat"
    file "Install_virtual_cam\Uninstall.bat"
    file "Install_virtual_cam\UnityCaptureFilter32bit.dll"
    file "Install_virtual_cam\UnityCaptureFilter64bit.dll"
    
    ; Uninstaller - see function un.onInit and section "uninstall" for configuration
    writeUninstaller "$INSTDIR\uninstall.exe"
    
    ; Start Menu entries
    createDirectory "$SMPROGRAMS\${APPNAME}"
    createShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\WebCamClone.exe" "" "$INSTDIR\wc.ico"
    createShortCut "$SMPROGRAMS\${APPNAME}\Uninstall ${APPNAME}.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe"
    
    ; Desktop shortcut
    createShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\WebCamClone.exe" "" "$INSTDIR\wc.ico"
    
    ; Registry information for add/remove programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME} - ${DESCRIPTION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$\"$INSTDIR\wc.ico$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "$\"${COMPANYNAME}$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "HelpLink" "$\"${HELPURL}$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLUpdateInfo" "$\"${UPDATEURL}$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "$\"${ABOUTURL}$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "$\"${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}$\""
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
    
    ; Show installation complete message
    MessageBox MB_OK "WebCamClone has been installed successfully!$\n$\nPlease note: You may need to install the virtual camera driver separately using the 'Install Virtual Camera' button in the application."
SectionEnd

; Uninstaller
function un.onInit
    SetShellVarContext all
    MessageBox MB_OKCANCEL "Are you sure you want to remove ${APPNAME} and all of its components?" IDOK next
        Abort
    next:
functionEnd

section "uninstall"
    ; Remove Start Menu launcher
    delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
    delete "$SMPROGRAMS\${APPNAME}\Uninstall ${APPNAME}.lnk"
    ; Try to remove the Start Menu Programs directory
    rmDir "$SMPROGRAMS\${APPNAME}"
    
    ; Remove Desktop shortcut
    delete "$DESKTOP\${APPNAME}.lnk"
    
    ; Remove files
    delete $INSTDIR\WebCamClone.exe
    delete $INSTDIR\wc.ico
    delete $INSTDIR\LICENSE
    delete $INSTDIR\README.md
    delete $INSTDIR\Install_virtual_cam\Install.bat
    delete $INSTDIR\Install_virtual_cam\InstallCustomName.bat
    delete $INSTDIR\Install_virtual_cam\InstallMultipleDevices.bat
    delete $INSTDIR\Install_virtual_cam\Uninstall.bat
    delete $INSTDIR\Install_virtual_cam\UnityCaptureFilter32bit.dll
    delete $INSTDIR\Install_virtual_cam\UnityCaptureFilter64bit.dll
    
    ; Remove directories
    rmDir $INSTDIR\Install_virtual_cam
    rmDir $INSTDIR
    
    ; Remove uninstaller information from the registry
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
    
    MessageBox MB_OK "WebCamClone has been uninstalled successfully!$\n$\nNote: The virtual camera driver may still be installed. If you want to remove it, please run the Uninstall.bat file from the Install_virtual_cam directory before uninstalling."
sectionEnd

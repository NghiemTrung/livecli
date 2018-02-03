#!/usr/bin/env bash
# Execute this at the base of the livecli repo.

set -e # stop on error

command -v makensis > /dev/null 2>&1 || { echo >&2 "makensis is required to build the installer. Aborting."; exit 1; }
command -v pynsist > /dev/null 2>&1 || { echo >&2 "pynsist is required to build the installer. Aborting."; exit 1; }

LIVECLI_ASSET_BASE=${LIVECLI_ASSET_BASE:-"https://raw.githubusercontent.com/livecli/assets/master"}
# For travis nightly builds generate a version number with commit hash
LIVECLI_VERSION=$(python setup.py --version)
LIVECLI_VERSION_PLAIN="${LIVECLI_VERSION%%+*}"
LIVECLI_INSTALLER="livecli-${LIVECLI_VERSION}"

# include the build number
LIVECLI_VI_VERSION="${LIVECLI_VERSION_PLAIN}.${TRAVIS_BUILD_NUMBER:-0}"

build_dir="$(pwd)/build"
nsis_dir="${build_dir}/nsis"
# get the dist directory from an environment variable, but default to the build/nsis directory
dist_dir="${LIVECLI_INSTALLER_DIST_DIR:-$nsis_dir}"
mkdir -p "${build_dir}" "${dist_dir}" "${nsis_dir}"

echo "Building livecli-${LIVECLI_VERSION} package..." 1>&2
python setup.py build 1>&2

echo "Building ${LIVECLI_INSTALLER} installer..." 1>&2

cat > "${build_dir}/livecli.cfg" <<EOF
[Application]
name=Livecli
version=${LIVECLI_VERSION}
entry_point=livecli_cli.main:main
icon=../win32/livecli.ico

[Python]
version=3.5.2
format=bundled

[Include]
; dep tree
;   livecli+livecli_cli
;       - pkg-resources (indirect)
;           - pyparsing
;           - packaging
;           - six
;       - iso639
;       - iso3166
;       - pycryptodome
;       - requests
;           - certifi
;           - idna
;           - urllib3
;           - socks / sockshandler
;       - websocket-client
packages=pkg_resources
         six
         iso639
         iso3166
         requests
         urllib3
         idna
         chardet
         certifi
         websocket
         socks
         sockshandler
pypi_wheels=pycryptodome==3.4.3

files=../win32/LICENSE.txt > \$INSTDIR
      ../build/lib/livecli > \$INSTDIR\pkgs
      ../build/lib/livecli_cli > \$INSTDIR\pkgs

[Command livecli]
entry_point=livecli_cli.main:main

[Build]
directory=nsis
nsi_template=installer_tmpl.nsi
installer_name=${dist_dir}/${LIVECLI_INSTALLER}.exe
EOF

cat >"${build_dir}/installer_tmpl.nsi" <<EOF
!include "FileFunc.nsh"
!include "TextFunc.nsh"
[% extends "pyapp_msvcrt.nsi" %]

[% block modernui %]
    ; let the user review all changes being made to the system first
    !define MUI_FINISHPAGE_NOAUTOCLOSE
    !define MUI_UNFINISHPAGE_NOAUTOCLOSE

    ; add checkbox for opening the documentation in the user's default web browser
    !define MUI_FINISHPAGE_RUN
    !define MUI_FINISHPAGE_RUN_TEXT "Open online manual in web browser"
    !define MUI_FINISHPAGE_RUN_FUNCTION "OpenDocs"
    !define MUI_FINISHPAGE_RUN_NOTCHECKED

    ; make global installation mode the default choice
    ; see MULTIUSER_PAGE_INSTALLMODE macro below
    !undef MULTIUSER_INSTALLMODE_DEFAULT_CURRENTUSER

    Function OpenDocs
        ExecShell "" "https://livecli.github.io/cli.html"
    FunctionEnd

    ; add checkbox for editing the configuration file
    !define MUI_FINISHPAGE_SHOWREADME
    !define MUI_FINISHPAGE_SHOWREADME_TEXT "Edit configuration file"
    !define MUI_FINISHPAGE_SHOWREADME_FUNCTION "EditConfig"
    !define MUI_FINISHPAGE_SHOWREADME_NOTCHECKED

    Function EditConfig
        SetShellVarContext current
        Exec '"\$WINDIR\notepad.exe" "\$APPDATA\livecli\liveclirc"'
        SetShellVarContext all
    FunctionEnd

    ; constants need to be defined before importing MUI
    [[ super() ]]

    ; Add the product version information
    VIProductVersion "${LIVECLI_VI_VERSION}"
    VIAddVersionKey /LANG=\${LANG_ENGLISH} "ProductName" "Livecli"
    VIAddVersionKey /LANG=\${LANG_ENGLISH} "CompanyName" "Livecli"
    VIAddVersionKey /LANG=\${LANG_ENGLISH} "FileDescription" "Livecli Installer"
    VIAddVersionKey /LANG=\${LANG_ENGLISH} "LegalCopyright" ""
    VIAddVersionKey /LANG=\${LANG_ENGLISH} "FileVersion" "${LIVECLI_VERSION}"
[% endblock %]

; UI pages
[% block ui_pages %]
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MULTIUSER_PAGE_INSTALLMODE
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
[% endblock ui_pages %]

[% block sections %]
[[ super()  ]]
SubSection /e "Bundled tools" bundled
    Section "rtmpdump" rtmpdump
        SetOutPath "\$INSTDIR\rtmpdump"
        File /r "rtmpdump\*.*"
        SetShellVarContext current
        \${ConfigWrite} "\$APPDATA\livecli\liveclirc" "rtmpdump=" "\$INSTDIR\rtmpdump\rtmpdump.exe" \$R0
        SetShellVarContext all
        SetOutPath -
    SectionEnd

    Section "FFMPEG" ffmpeg
        SetOutPath "\$INSTDIR\ffmpeg"
        File /r "ffmpeg\*.*"
        SetShellVarContext current
        \${ConfigWrite} "\$APPDATA\livecli\liveclirc" "ffmpeg-ffmpeg=" "\$INSTDIR\ffmpeg\ffmpeg.exe" \$R0
        SetShellVarContext all
        SetOutPath -
    SectionEnd
SubSectionEnd
[% endblock %]

[% block install_files %]
    [[ super() ]]
    ; Install config file
    SetShellVarContext current # install the config file for the current user
    SetOverwrite off # config file we don't want to overwrite
    SetOutPath \$APPDATA\livecli
    File /r "liveclirc"
    SetOverwrite ifnewer
    SetOutPath -
    SetShellVarContext all

    ; Add metadata
    ; hijack the install_files block for this
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\\${PRODUCT_NAME}" "DisplayVersion" "${LIVECLI_VERSION}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\\${PRODUCT_NAME}" "Publisher" "Livecli"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\\${PRODUCT_NAME}" "URLInfoAbout" "https://livecli.github.io/"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\\${PRODUCT_NAME}" "HelpLink" "https://livecli.github.io/"
    \${GetSize} "\$INSTDIR" "/S=0K" \$0 \$1 \$2
    IntFmt \$0 "0x%08X" \$0
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\\${PRODUCT_NAME}" "EstimatedSize" "\$0"
[% endblock %]

[% block uninstall_files %]
    [[ super() ]]
    RMDir /r "\$INSTDIR\rtmpdump"
    RMDir /r "\$INSTDIR\ffmpeg"
[% endblock %]

[% block install_commands %]
    ; Remove any existing bin dir from %PATH% to avoid duplicates
    [% if has_commands %]
    nsExec::ExecToLog '[[ python ]] -Es "\$INSTDIR\_system_path.py" remove "\$INSTDIR\bin"'
    [% endif %]
    [[ super() ]]
[% endblock install_commands %]

[% block install_shortcuts %]
    ; Remove shortcut from previous releases
    Delete "\$SMPROGRAMS\Livecli.lnk"
[% endblock %]

[% block uninstall_shortcuts %]
    ; no shortcuts to be removed...
[% endblock %]

[% block mouseover_messages %]
[[ super() ]]

StrCmp \$0 \${sec_app} "" +2
  SendMessage \$R0 \${WM_SETTEXT} 0 "STR:\${PRODUCT_NAME} with embedded Python"

StrCmp \$0 \${bundled} "" +2
  SendMessage \$R0 \${WM_SETTEXT} 0 "STR:Extra tools used to play some streams"

StrCmp \$0 \${rtmpdump} "" +2
  SendMessage \$R0 \${WM_SETTEXT} 0 "STR:rtmpdump is used to play RTMP streams"

StrCmp \$0 \${ffmpeg} "" +2
  SendMessage \$R0 \${WM_SETTEXT} 0 "STR:FFMPEG is used to mux separate video and audio streams, for example high quality YouTube videos or DASH streams"

[% endblock %]
EOF

echo "Building Python 3 installer" 1>&2

# copy the liveclirc file to the build dir, we cannot use the Include.files property in the config file
# because those files will always overwrite, and for a config file we do not want to overwrite
cp "win32/liveclirc" "${nsis_dir}/liveclirc"

# copy the ffmpeg and rtmpdump directories to the install build dir
cp -r "win32/ffmpeg" "${nsis_dir}/"
cp -r "win32/rtmpdump" "${nsis_dir}/"

# Downloading external assets
wget -c -O "${nsis_dir}/ffmpeg/ffmpeg.exe" "${LIVECLI_ASSET_BASE}/win32/ffmpeg/ffmpeg.exe"
wget -c -O "${nsis_dir}/rtmpdump/rtmpdump.exe" "${LIVECLI_ASSET_BASE}/win32/rtmpdump/rtmpdump.exe"
wget -c -O "${nsis_dir}/rtmpdump/librtmp.dll" "${LIVECLI_ASSET_BASE}/win32/rtmpdump/librtmp.dll"

pynsist build/livecli.cfg

echo "Success!" 1>&2
echo "The installer should be in ${dist_dir}." 1>&2

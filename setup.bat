@echo off
rem -------------------------------------------------
rem Setup script for MergeApp – Windows
rem -------------------------------------------------
set "APPDATA_DIR=%APPDATA%\\MergeApp"
if not exist "%APPDATA_DIR%" mkdir "%APPDATA_DIR%"

rem Copy default icon (allows user to replace later)
copy /Y "icone\\icone.ico" "%APPDATA_DIR%\\custom_icon.ico" >nul

rem Record current version for update checks
echo v1.2.0 > "%APPDATA_DIR%\\current_version.txt"

echo Setup concluído. Execute "MergeApp.exe" para iniciar o aplicativo.
pause

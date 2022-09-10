@echo off

if defined quik_setup ( goto :run )

set quik_setup=1
doskey quik=%~f0 $*

:run

setlocal EnableDelayedExpansion
set rootdir=%~dp0

set quik_py=%rootdir%\..\quik.py
set parse_py=%rootdir%\output_parse.py
set quik_json=%rootdir%\..\quik.json
set out=
set userout=
set cdout=
set nl=^


REM do not remove the two empty lines above
for /F "delims=*" %%i in ('python %quik_py% %*') do (
    if "!out!"=="" (set out=%%i) else (set out=!out!!nl!%%i)
)
set retcode=%errorlevel%

if %retcode% NEQ 0 (
    echo Quik had an error:
    echo !out!
    endlocal
    goto :eof
)

(echo !out! | findstr /l "+cd ") >nul 2>&1
if %errorlevel%==0 (
    for /F "delims=*" %%i in ('echo !out! ^| python %parse_py% --output 2^>^&1') do if "!userout!"=="" (set userout=%%i) else (set userout=!userout!!nl!%%i)
    if "!userout!" NEQ "" (echo !userout!)

    for /F "delims=*" %%i in ('echo !out! ^| python %parse_py% --cd 2^>^&1') do set cdout=%%i

    REM HACK to survive endlocal
    for /f "tokens=1 delims=" %%A in (""!cdout!"") do (
        endlocal
        cd /D %%A
        goto :eof
    )
) else (
    if "!out!" NEQ "" (echo !out!)
)

endlocal

:eof

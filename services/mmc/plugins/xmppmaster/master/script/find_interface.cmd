@echo off
setlocal EnableDelayedExpansion
for /f "delims=" %%L in ('ipconfig') do (
    echo %%L | findstr /r "^[A-Z]" 1>NUL
    if !errorlevel! == 0 set "_int=%%L"
    echo %%L | findstr /c:%1 1>NUL
    if !errorlevel! == 0 (
       set "_int=!_int::=!"
       echo !_int:* adapter =!
       goto:eof
    )
)
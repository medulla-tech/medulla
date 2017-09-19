@echo off
setlocal
setlocal enabledelayedexpansion
set "_adapter="
set "_ip="
for /f "tokens=1* delims=:" %%g in ('ipconfig /all') do (
  set "_tmp=%%~g"
  if "!_tmp:adapter=!"=="!_tmp!" (
    if not "!_tmp:IPv4 Address=!"=="!_tmp!" (
      for %%i in (%%~h) do (
      if not "%%~i"=="" set "_ip=%%~i"
      )
    set "_ip=!_ip:(Preferred)=!"
    if "!_ip!"=="%1" (
        @echo !_adapter!
      )
    )
  ) else (
    set "_ip="
    set "_adapter=!_tmp:*adapter =!"
  )
)
endlocal

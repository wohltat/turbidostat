@echo off
echo Turbidostat firmware updater
echo ----------------------------
set /p port="Enter port (e.g. COM1): "
echo Updating firmware on device at port %1
cd firmware
@echo on
avrdude.exe -Cavrdude.conf -v -V -patmega328p -carduino -P%port% -b57600 -D -Uflash:w:turbidostat_v0332.ino.hex:i 
pause
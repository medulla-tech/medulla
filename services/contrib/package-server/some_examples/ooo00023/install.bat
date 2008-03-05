@echo off
echo Debut de l'installation
chmod ugo+rx *
mkdir java
copy jre-6u3-windows-i586-p.exe java
msiexec.exe /i openofficeorg23.msi /qn /l* OOo2.log.txt
echo Installation terminee.
more OOo2.log.txt
rm -f java\jre-6u3-windows-i586-p.exe
rmdir java
rm -f OOo2.log.txt

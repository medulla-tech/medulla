@echo off
echo Debut de l'installation
chmod ugo+rx *
msiexec.exe /i openofficeorg20.msi /qn /l* OOo2.log.txt
echo Installation terminee.
more OOo2.log.txt
rm -f OOo2.log.txt

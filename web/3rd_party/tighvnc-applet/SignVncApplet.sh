export JAVA_HOME=/usr/lib/j2sdk1.5-sun
export PATH=$JAVA_HOME/bin:$PATH

DN="cn=Mandriva Pulse 2,OU=Pulse 2 Team,O=Mandriva S.A.,L=Paris,S=France,C=FR"
NAME=VncViewer

cp -a ../../msc/graph/java/$NAME.jar .
jar tvf $NAME.jar

rm $NAME.keystore
keytool -genkey -keyalg dsa -keysize 1024 -validity 3650 -dname "$DN" -keystore $NAME.keystore -alias "Pulse 2 - $NAME"

jarsigner -keystore $NAME.keystore -verbose $NAME.jar "Pulse 2 - $NAME"
jarsigner -verify -verbose -certs $NAME.jar


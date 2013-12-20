python.exe setup.py build
cp -r conf build/exe\.win*/
mv build/exe\.win*/conf/pull_client.conf.example build/exe\.win*/conf/pull_client.conf

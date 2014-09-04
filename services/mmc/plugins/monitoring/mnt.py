import nmap
import sys
import os


def get_host_os(ip):
	try:
	    nm = nmap.PortScanner()         
	except nmap.PortScannerError:
    		print('Nmap not found', sys.exc_info()[0])
    		sys.exit(0)
	except:
    		print("Unexpected error:", sys.exc_info()[0])
    		sys.exit(0)
	if (os.getuid() != 0):
		return 0

	nm.scan(ip, arguments='-O')

        if nm[ip].has_key('osmatch'):
                for osmatch in nm[ip]['osmatch']:
                        print('OsMatch.name : {0}'.format(osmatch['name']))
                        print('OsMatch.accuracy : {0}'.format(osmatch['accuracy']))
                        print('OsMatch.line : {0}'.format(osmatch['line']))
                        print('')
                return nm[ip]['osmatch']

	if nm[ip].has_key('osclass'):
	        for osclass in nm[ip]['osclass']:
	            	print('OsClass.type : {0}'.format(osclass['type']))
        	    	print('OsClass.vendor : {0}'.format(osclass['vendor']))
			print('OsClass.osfamily : {0}'.format(osclass['osfamily']))
			print('OsClass.osgen : {0}'.format(osclass['osgen']))
            		print('OsClass.accuracy : {0}'.format(osclass['accuracy']))
           		print('')
		return nm[ip]['osclass']


	if nm[ip].has_key('fingerprint'):
        	print('Fingerprint : {0}'.format(nm[ip]['fingerprint']))
		return nm[ip]['fingerprint']

	return 0

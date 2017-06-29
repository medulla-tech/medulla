Pulse2
======

Pulse 2 helps organizations ranging from a few computers to 100 000+
heterogeneous computers to inventory, maintain, update and take full
control on their IT assets. It has been designed to handle 100 000+
computers spread on many sites.  It supports heterogeneous platforms
such as MS Windows, GNU/Linux (Mandriva, Redhat, Debian, Ubuntu.,
etc.), Mac OSX, HP-UX, IBM AIX and Solaris systems.

Configuration
~~~~~~~~~~~~~

Pulse2 is designed in a very distributed way, involving several agents
running together on the same machine or not. See Installation

Installation
~~~~~~~~~~~~~
Installation process had been simplified to easily install all differents components from one command line.

Check here :

https://github.com/pulse-project/tools/tree/master/install

Pulse2 clients
~~~~~~~~~~~~~~

* Win32:

  A complete win32 client agent pack can be built with the script 
  
  /var/lib/pulse2/clients/win32/generate-agent-pack.sh

* Linux and Mac

  A script is available to build it automatically
  
  /var/lib/pulse2/clients/generate-agent.sh

All agents will be available for downloads from http://ippulseserver/downloads/



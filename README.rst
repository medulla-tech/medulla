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
running together on the same machine or not. Each agent having its own 
configuration file, you can use the `pulse2-setup' to setup major 
configuration options automatically.

This tool is also responsible for provisioning databases and checking
mmc-core LDAP setup.

To use it, simply type `pulse2-setup` and answer the questions.

The following options can be used:
`--help`
`-h`
    Print a summary of all the options, and exit.

`--debug`
`-d`
    Print debug messages.

`--batch`
`-b`
    Do not ask any questions. Defaults values are taken from:
    - existing configuration files, if any
    - if not, working default values

`--reset`
`-R`
    Reset all Pulse2 configuration and start from default values.

`--pkgdatadir=DIR`
    Look into DIR for sql snippets and so on. Default to /usr/share/pulse2

`--confdir=DIR`
   Path to configuration directory. Default to /etc/mmc

Pulse2 clients
~~~~~~~~~~~~~~

* Win32:
  A complete win32 client agent pack can be built with the script 
  /var/lib/pulse2/clients/win32/generate-agent-pack.sh

  It takes as only argument path to the ssh public key to include into the pack.

Pulse2 misc documentation
~~~~~~~~~~~~~~~~~~~~~~~~~

For some documentations, scripts, how-to and more, `click here <https://www.dropbox.com/sh/wgn4yckax8083tg/AACb7sfP2jnft8prhSrafumNa>`_.

# A simple setup script for creating a Windows service. See the comments in the
# Config.py and ServiceHandler.py files for more information on how to set this
# up.
#
# Installing the service is done with the option --install <Name> and
# uninstalling the service is done with the option --uninstall <Name>. The
# value for <Name> is intended to differentiate between different invocations
# of the same service code -- for example for accessing different databases or
# using different configuration files.

from cx_Freeze import setup, Executable

buildOptions = dict(includes=["service", "dlp"], include_msvcr=1)
executable = Executable("config.py", base = "Win32Service",
        targetName = "service.exe")

setup(
        name = "pulse_pull_client",
        version = "0.1",
        description = "Pulse service for Pull-mode deployment",
        executables = [executable],
        options = dict(build_exe = buildOptions))

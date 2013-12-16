from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [], include_msvcr = 1)
# Application type is console
base = 'Console'

executables = [
    Executable('pulse-update-manager.py', base=base)
]

setup(name='Pulse Update Manager',
      version = '1.0',
      description = 'Pulse Update Manager',
      options = dict(build_exe = buildOptions),
      executables = executables)

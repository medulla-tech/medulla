from distutils.core import setup

setup(
    name = "mmc-agent",
    version = "1.0",
    url = "http://www.mandriva.com",
    author = "Cedric Delfosse",
    author_email = "cdelfosse@mandriva.com",
    maintainer = "Cedric Delfosse",
    maintainer_email = "cdelfosse@mandriva.com",
    packages = ["mmc", "mmc.support", "mmc.plugins", "mmc.plugins.base", "mmc.plugins.samba", "mmc.plugins.proxy", "mmc.plugins.mail", "mmc.plugins.network"],
)

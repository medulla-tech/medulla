from distutils.core import setup

setup(
    name = "lmc-agent",
    version = "1.0",
    url = "http://www.linbox.com",
    author = "Cedric Delfosse",
    author_email = "cedric.delfosse@linbox.com",
    maintainer = "Cedric Delfosse",
    maintainer_email = "cedric.delfosse@linbox.com",
    packages = ["lmc", "lmc.support", "lmc.plugins", "lmc.plugins.base", "lmc.plugins.samba", "lmc.plugins.proxy", "lmc.plugins.mail", "lmc.plugins.network"],
)

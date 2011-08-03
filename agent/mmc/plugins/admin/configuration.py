"""
Various functions to get values from config files and
to edit these values.
"""

from mmc.support.config import PluginConfigFactory
from mmc.agent import PluginManager
from mmc.plugins.inventory.config import InventoryConfig
from mmc.plugins.glpi.config import GlpiConfig

def get_conf_array(name):
    config = PluginConfigFactory.get(name)
    array = {}
    for section in config.sections():
        config.options(section)
        dic = {}
        for opt in config.options(section):
            dic[opt] = config.get(section, opt)
        array[section] = dic
    return array

def set_conf_array(args):
    print(args)
    name, values = args['filename'], args['values']
    config = PluginConfigFactory.get(name)
    for option_name in values:
        section_name = values[option_name]['section_name']
        value = values[option_name]['value']
        if not config.has_section(section_name):
            config.add_section(section_name)
        config.set(section_name, option_name, value)
    # TODO check if the conf is OK, and return an error message if not
    return True

def switchInventoryModule(module_name):
    """
    Activate the new Inventory method and deactivate the other.
    Returns a tuple: True or False and an error message
    describing the reason why it failed.
    """
    pm = PluginManager()
    pm.startPlugin(module_name)
    if module_name == 'inventory':
        pm.stopPlugin('glpi')
    else:
        pm.stopPlugin('inventory')
    return (True,)

def loadInventoryConf(module_name):
    """
    before commiting the config for the inventory module
    we are switching to, we make sure the config is loaded
    (if not we load it), to be able to modify its value
    before starting the module
    Also enable and disable the correct module (but they
    are not yet started, just the config is modified)
    """
    pm = PluginManager()
    inventory_config = PluginConfigFactory.new(InventoryConfig, "inventory")
    glpi_config = PluginConfigFactory.new(GlpiConfig, "glpi")
    print('Instance of inventory config in loadInventoryConf is %s' % inventory_config)


    # Enable and disable the right modules in their config
    base_config = PluginConfigFactory.get("base")
    # base_config.set('computers', 'method', module_name)
    glpi_config.set('main', 'disable', '0' if module_name == 'glpi' else 1)
    inventory_config.init('inventory')
    inventory_config.cp.set('main', 'disable', '0' if module_name == 'inventory' else 1)

    print('Disable: ', inventory_config.disable)

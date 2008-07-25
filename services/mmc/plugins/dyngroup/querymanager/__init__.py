import os
import re
import logging

from mmc.plugins.dyngroup.database import DyngroupDatabase
from mmc.plugins.dyngroup.config import DGConfig
import mmc

def activate():
    conf = DGConfig("dyngroup")

    DyngroupDatabase().activate()
    if conf.disable:
       return False
       
    return conf.dyngroup_activate

def queryPossibilities():
    ret = {}
    ret['groupname'] = ['list', getAllGroupName]
    return ret

def query(ctx, criterion, value):
    logging.getLogger().info(ctx)
    logging.getLogger().info(criterion)
    logging.getLogger().info(value)
    machines = []
    if criterion == 'groupname':
        machines = map(lambda x: x.name, DyngroupDatabase().getMachines(ctx, {'gname':value}))
    return [machines, True]

def getAllGroupName(ctx, value = ''):
    return map(lambda x:x.name, DyngroupDatabase().getallgroups(ctx, {'filter':value}))

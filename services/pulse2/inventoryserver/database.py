# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from mmc.plugins.inventory.config import InventoryExpertModeConfig, InventoryConfig
from mmc.plugins.inventory.utilities import unique, getInventoryParts, getInventoryNoms
from mmc.plugins.inventory.database import *
from pulse2.inventoryserver.mapping import OcsMapping


class InventoryWrapper(Inventory):
    def createNewInventory(self, hostname, inventory, date):
        # TODO : check that inventory is not empty....
        k = 0
        for i in map(lambda x: len(inventory[x]), inventory):
            k = i+k
        if k == 0:
            return False
            
        date = date.split(' ')
        
        session = create_session()
        transaction = session.create_transaction()
        try: 
            m = self.getMachinesOnly(None, {'hostname':hostname}) # TODO uuids!
            if len(m) == 0:
                m = Machine()
                m.Name = hostname
                session.save(m)
            elif len(m) > 1:
                session.close()
                return False
            else:
                m = m[0]
            result = session.query(InventoryTable).select_from(self.inventory.join(self.table['hasHardware']).join(self.machine)).filter(self.machine.c.Name == hostname)
            for inv in result:
                inv.Last = 0
                session.save(inv)
            i = InventoryTable()
            i.Date, i.Time = date
            i.Last = 1
            session.save(i)
            session.flush()
            
            for table in inventory:
                content = inventory[table]
                tname = table.lower()
                if len(content) == 0:
                    continue
                
                klass = self.klass[table]
                hasKlass = self.klass['has'+table]
                hasTable = self.table['has'+table]
                
                h = hasTable.insert()
                for cols in content:
                    try:
                        if len(cols) == 0:
                            continue
                        id = self.getIdInTable(table, cols, session)
                        if id == None:
                            k = klass()
                            for col in cols:
                                if type(col) == str or type(col) == unicode:
                                    setattr(k, col, cols[col])
                            session.save(k)
                            session.flush()
                            id = k.id
                        
                        nids = {}
                        if OcsMapping().nomenclatures.has_key(table):
                            for nom in OcsMapping().nomenclatures[table]:
                                self.logger.debug("1 %s"%(str(nom)))
                                self.logger.debug("1.1 %s"%(str(cols)))
                                nomName = 'nom%s%s' % (table, nom)
                                nomKlass = self.klass[nomName]
                                nomTable = self.table[nomName]
                                
                                ncols = {}
                                for col in cols:
                                    if type(col) == tuple and col[0] == nomName:
                                        ncols[col[1]] = cols[col]
                                self.logger.debug("1.2 %s"%(str(ncols)))
                                
                                nid = self.getIdInTable(nomName, ncols, session)
                                self.logger.debug("1.3 %s"%(str(nid)))
                                if nid == None:
                                    n = nomKlass()
                                    for col in ncols:
                                        setattr(n, col, ncols[col])
                                    session.save(n)
                                    session.flush()
                                    nid = n.id
                                nids[nom] = nid
                            self.logger.debug("2 %s"%(str(nids)))
                        
                        params = {'machine':m.id, 'inventory':i.id, tname:id}
                        if len(nids.keys()) > 0:
                            for nom in nids:
                                params[nom.lower()] = nids[nom]
                        has = self.isElemInTable('has'+table, params, session)
                        if has == None or has == 0:
                            h.execute(params)
                            # we should flush the session, but as it is not absolutly needed here,
                            # and it takes a lot of time, we will do it later.
                    except UnicodeDecodeError, e: # just for test
                        pass
                    except Exception, e:
                        logging.getLogger().error(e)
                        pass
        except KeyError, e:
            transaction.rollback()
            session.close()
            logging.getLogger().error(e.args)
            raise e
        except Exception, e:
            transaction.rollback()
            session.close()
            logging.getLogger().error(e)
            raise e

        session.flush()
        transaction.commit()
        session.close()
        return True


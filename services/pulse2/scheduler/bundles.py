# -*- coding: utf-8; -*-
#
# (c) 2013 Mandriva, http://www.mandriva.com/
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

""" This module provides a bundle tracking to priority order control."""

import logging


class BundleElement :
    """ 
    A simple table of references of one circuit. 

    This is a simple clone of relations of ids defined in the database,
    which is used as element in the main bundle references table.
    """
    # bundle.id
    id = None
    # commands.id
    cmd_id = None
    # commands_on_host.id
    coh_id = None
    # commands.order_in_bundle
    order = None
    # target.id
    targer_id = None

    # if circuit finished (commands_on_host.current_state == "done")
    # then True, otherwise False
    finished = False


    def __init__(self, id, cmd_id, coh_id, order, target_uuid):
        self.id = id
        self.cmd_id = cmd_id
        self.coh_id = coh_id
        self.order = order
        self.target_uuid = target_uuid

        self.finished = False


class BundleReferences :
    """
    Central bundle processing.

    This container stocks all the bundle relations and controls
    the order processing.
    """

    content = []

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger()

    @property
    def all_ids(self):
        """
        property getter to return all bundle ids.

        @return: all bundle ids
        @rtype: list
        """
        ids = []
        for c in self.content :
            if c.id not in ids:
                ids.append(c.id)
        return ids


    def update(self, circuit, finished=False):
        """
        Inserts or updates the circuit which is a part of a bundle.

        @param circuit: circuit to insert or update
        @type circuit: Circuit
        """
        if circuit.cohq.cmd.fk_bundle :
            c = circuit.cohq
            if c.coh.id not in [b.coh_id for b in self.content] :
                self.logger.debug("Circuit #%s: added to bundle control" % circuit.id)
                bundle = BundleElement(c.cmd.fk_bundle, 
                                       circuit.cmd_id,
                                       circuit.id,
                                       c.cmd.order_in_bundle,
                                       c.target.target_uuid)
                bundle.finished = finished
                self.content.append(bundle)
            else :

                matches = self.get(coh_id=c.coh.id)
                if len(matches) == 1 :
                    bundle = matches[0]
                    bundle.finished = finished
                else :
                    self.logger.warn("Circuit #%s: multiple entries in the bundle control" % circuit.id)
 
    def finish(self, coh_id):
        """
        Flagging the circuit as finished.

        @param coh_id: commands_on_host id
        @type coh_id: int
        """
        matches = self.get(coh_id=coh_id)
        if len(matches)==1:
            b = matches[0]
            b.finished = True
            self.logger.debug("Circuit #%s: of bundle #%s finished (order=%d)" %  
                    (coh_id, b.id, b.order))


    def get(self, **kwargs):
        """ 
        Gets a BundleElement or more. 

        The kwargs must containing at least one of bundle filter.
        """

        content = self.content
        for key, value in kwargs.items():
            content = [b for b in content if getattr(b, key)==value]

        return content

    def get_next_in_order(self, coh_id):
        """
        Gets the next ready circuit.

        @param coh_id: commands_on_host id
        @type coh_id: int
        """

        matches = self.get(coh_id=coh_id)
        if len(matches)==1:
            actual = matches[0]
            next = self.get(id = actual.id, 
                            target_uuid = actual.target_uuid,
                            order = actual.order + 1)
            if len(next)==1 :
                return next[0]
            else :
                return None
        else :
            return None

    def is_last(self, coh_id):
        """
        Checks if requested circuit is the last in bundle.

        @param coh_id: commands_on_host id
        @type coh_id: int
        """
        if self.get_next_in_order(coh_id):
            return False
        else :
            return True

    def is_previous_finished(self, coh_id):
        """
        Checks if previous circuit of requested circuit was finished.

        @param coh_id: commands_on_host id
        @type coh_id: int
        """

        matches = self.get(coh_id=coh_id)
        if len(matches)==1:
            actual = matches[0]
            if actual.order == 1 :
                # im first, so let's go
                return True

            matches = self.get(id = actual.id, 
                               target_uuid = actual.target_uuid,
                               order = actual.order - 1)
 
            if len(matches)==1:
                previous = matches[0]
                return previous.finished
        return False  


    def get_ready_cohs(self):
        """
        @return: all circuit ids allowed to start.
        @rtype: list
        """
        return [c.coh_id for c in self.content if self.is_previous_finished(c.coh_id)
                                                   and not c.finished]
 

    def get_banned_cohs(self):
        """
        @return: all circuit ids denied to start.
        @rtype: list
        """
        return [c.coh_id for c in self.content if not self.is_previous_finished(c.coh_id)]
 
    def remove_bundle(self, id):
        """
        Removes the bundle, with all the circuit references from container.

        @param id: bundle id
        @type id: int
        """
        cohs = self.get(id=id)
        for coh in cohs :
            self.content.remove(coh)
        

    def clean_up_finished(self):
        """
        Removes all finished bundles.
        """
        for id in self.all_ids :
            finished = all([b.finished for b in self.content if b.id==id])
            if finished :
                self.logger.debug("Removing the bundle #%d from bundle processing" % id)
                for b in self.content :
                    self.content.remove(b)

    def clean_up_remaining(self, ids):
        """
        Removes all remaining bundles excluding running ids.

        @param ids: bundle ids to hold
        @type ids: list
        """
        for coh in self.content :
            if coh.id not in ids :
                self.logger.debug("Removing the circuit #%d from bundle processing" % coh.coh_id)
                self.content.remove(coh)


            
    def clean_up(self, **kwargs):
        """
        Removes all matching circuits.

        @param ids: commands_on_host ids
        @type ids: list
        """
        if "coh_id" in kwargs :
            coh_id = kwargs["coh_id"]
            cohs = self.get(coh_id=coh_id)
            for coh in cohs :
                self.content.remove(coh)

        if "cmd_ids" in kwargs :
            for cmd_id in kwargs["cmd_ids"] :
                cohs = self.get(cmd_id=cmd_id)
                for coh in cohs :
                    self.content.remove(coh)
 


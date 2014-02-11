#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Glpi rest client to interact with GLPI webservices plugin
# This program is part of python-glpi lib:
#
# https://github.com/mcphargus/python-glpi
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import urllib, urllib2
import json
import warnings

__name__ == "GLPIClient"

class RESTClient(object):
    """.. note:: If any boolean arguments are defined, they're \
    automatically added to the GET request, which means the \
    webservices API will treat them as being true. You've been warned. """

    """ URL part that comes after the hostname '/glpi' is the default """

    def __init__(self, baseurl="http://localhost/glpi"):
        self.baseurl = baseurl

    def __request__(self,params):
        return self.url + urllib.urlencode(params)

    def check_connected(self):
        """

        Gather informations from the current user to check that the session is
        still valid.

        Returns True if connection is still good.
        """

        my_infos = self.get_my_info()
        if my_infos.get('faultCode', 0) == 13:
            return False
        return True

    def load_session(self, host, session):
        """

        Connect with a previous session token to a running GLPI instance that
        has the webservices plugin enabled.

        Returns True if connection was successful.

        :type host: string
        :type session: string
        :param host: hostname of the GLPI server, has not been tested with HTTPS
        :param session: the session token
        """

        self.url = self.baseurl + '/plugins/webservices/rest.php?'
        self.session = session
        if self.check_connected():
            return True
        else:
            return False

    def connect(self,login_name=None,login_password=None):
        """

        Connect to a running GLPI instance that has the webservices
        plugin enabled.

        Returns True if connection was successful.

        :type host: string
        :type login_name: string
        :type login_password: string
        :param host: hostname of the GLPI server, has not been tested with HTTPS
        :param login_name: your GLPI username
        :param login_password: your GLPI password
        """

        self.url = self.baseurl + '/plugins/webservices/rest.php?'

        self.login_name = None
        self.login_password = None
        if login_name: self.login_name = login_name
        if login_password: self.login_password = login_password

        if self.login_name != None and self.login_password != None:
            params = {'login_name':login_name,
                      'login_password':login_password,
                      'method':'glpi.doLogin'}
            request = urllib2.Request(self.url + urllib.urlencode(params))
            response = urllib2.urlopen(request).read()
            try:
                session_id = json.loads(response)['session']
                self.session = session_id
                return True
            except:
                raise Exception("Login incorrect or server down")
        else:
            warnings.warn("Connected anonymously, will only be able to use non-authenticated methods")
            return self

    """
    Un-authenticated methods
    """

    def get_server_status(self,_help=None):
        """
        Gets server status information from the GLPI server, mostly
        stating that things are OK.

        :type _help: bool
        :param _help: get usage information
        """
        params = {'method':'glpi.status'}
        if _help: params['help'] = _help
        request = urllib2.Request(self.url + urllib.urlencode(params))
        response = urllib2.urlopen(request).read()
        return json.loads(response)

    def test(self,_help=None):
        """
        Simple ping test method.

        Returns version information of GLPI and of plugins that provide methods

        :type _help: boolean
        :param _help: get usage information
        """
        params = {'method':'glpi.test'}
        if _help: params['help'] = _help
        request = urllib2.Request(self.url + urllib.urlencode(params))
        response = urllib2.urlopen(request).read()
        return json.loads(response)

    def list_all_methods(self,_help=None):
        """
        Returns a list of all methods allowed to the current client

        :type _help: boolean
        :param _help: get usage information
        """
        params = {'method':'glpi.listAllMethods'}
        if _help: params['help'] = _help
        request = urllib2.Request(self.url + urllib.urlencode(params))
        response = urllib2.urlopen(request).read()
        return json.loads(response)

    def list_entities(self,count=None,_help=None):
        """
        Returns a list of current entities defined by server
        configuration for the client, or currently B{activated} for
        the user (when authenticated)

        :type _help: boolean
        :param _help: get usage information
        """
        params = {'method':'glpi.listAllMethods'}
        if self.session: params['session'] = self.session
        if count:
            if len(count) < 2:
                raise Exception("List needs to include a start and limit integer")
            if len(count) == 2:
                params['start'] = count[0]
                params['limit'] = count[1]
        if _help: params['help'] = _help
        request = urllib2.Request(self.url + urllib.urlencode(params))
        response = urllib2.urlopen(request).read()
        return json.loads(response)

    def list_know_base_items(self, faq=None, category=None,
                             contains=None, count=None, _help=None):

        """
        Returns a list of Knowbase or FAQ items available for the
        current user (when authenticated) or in the public FAQ (if
        configured)

        :type faq: boolean
        :type category: integer
        :type contains: string
        :type count: list
        :type _help: boolean
        :param faq: defaults to 0, returns FAQ
        :param category: ID of the category to search in
        :param contains: string to search for
        :param count: iterable containing start and limit integers
        :param _help: get usage information
        """
        params = {'method':'glpi.listKnowBaseItems'}
        if self.session: params['session'] = self.session
        if faq: params['faq'] = faq
        if category: params['category'] = category
        if contains: params['contains'] = contains
        if count:
            if len(count) < 2:
                raise Exception("List needs to include a start and limit integer")
            if len(count) == 2:
                params['start'] = count[0]
                params['limit'] = count[1]
        if _help: params['help'] = _help
        request = urllib2.Request(self.url + urllib.urlencode(params))
        response = urllib2.urlopen(request).read()
        return json.loads(response)

    """
    User context methods
    """

    def get_my_info(self):
        """
        Returns JSON serialized information about the currently logged
        in user.
        """
        params = {'method':'glpi.getMyInfo',
                  'session':self.session}
        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def list_my_profiles(self):
        """
        Returns JSON serialized profile information about the
        currently logged in user.
        """
        params = {'method':'glpi.listMyProfiles',
                  'session':self.session}
        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def list_my_entities(self):
        """
        Returns JSON serialized informations about the entities of the
        currently logged in user.
        """
        params = {'method':'glpi.listMyEntities',
                  'session':self.session}
        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    """
    Information retrieval methods
    """

    def get_ticket(self,ticket_id,id2name=None,_help=None):
        """
        Returns a JSON serialized ticket

        :type ticket_id: integer
        :type id2name: string
        :type _help: boolean
        :param ticket_id: ID of the ticket being requested
        :param id2name: option to enable id to name translation of dropdown fields
        :param _help: return JSON serialized help about the API call
        """
        params = {'method':'glpi.getTicket',
                  'ticket':ticket_id,
                  'session':self.session}
        if id2name: params['id2name'] = str(id2name)
        if _help: params['help'] = help

        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def get_object(self,itemtype,_id,show_label=None,
                     show_name=None,_help=None):
        """
        Returns an object from the GLPI server. itemtype can take `one of the following <https://forge.indepnet.net/embedded/glpi/annotated.html>`_

        :type itemtype: integer
        :type _id: integer
        :type show_label: boolean
        :type show_name: boolean
        :type _help: boolean
        :param itemtype: type of the item being requested
        :param _id: ID of the item being requested
        :param show_label: show label
        :param show_name: show name
        :param _help: get usage information

        """
        params = {'method':'glpi.getObject',
                  'session':self.session}

        if itemtype: params['itemtype'] = itemtype
        if _id: params['id'] = _id
        if show_label: params['show_label'] = show_label
        if show_name: params['show_name'] = show_name
        if _help: params['help'] = _help
        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def get_computer(self,computer_id,**kwargs):
        """
        Returns a JSON serialized computer object from the GLPI server

        :type computer_id: integer
        :type id2name: boolean
        :type infocoms: boolean
        :type contracts: boolean
        :type networkports: boolean
        :type help: boolean
        :param computer_id: computerID
        :param id2name: option to enable id to name translation of dropdown fields
        :param infocoms: return infocoms associated with the computer
        :param contracts: return contracts associated with the network equipment
        :param networkports: return information about computer's network ports
        :param help: get usage information
        """
        params = {'method':'glpi.getComputer',
                  'session': self.session,
                  'computer':computer_id}

        ###################### Tue Oct  9 17:22:34 EDT 2012 ##############
        # I realized today that I don't like to type very much, using
        # kwargs is cleaner, if anyone has a major issue with that,
        # speak now or forever hold your peace. -CDG
        ################ old stuff here ##################################
        # print self.__request__(params)
        # if id2name: params['id2name'] = id2name
        # if infocoms: params['infocoms'] = infocoms
        # if contracts: params['contracts'] = contracts
        # if networkports: params['networkports'] = networkports
        # if _help: params['help'] = _help

        for arg in kwargs:
            params[arg]  = kwargs[arg]

        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def get_computer_infocoms(self,computer_id,id2name=None,_help=None):
        """
        Return a JSON serialized list of computer infocoms from the
        GLPI server.

        :type computer_id: integer
        :type id2name: boolean
        :type _help: boolean
        :param computer_id: ID of the computer
        :param id2name: associate labels with IDs and return with the rest of the JSON result
        :param _help: return JSON serialized information about this API call
        """
        params = {'method':'glpi.getComputerInfoComs',
                  'session':self.session,
                  'id':computer_id}
        if id2name: params['id2name'] = id2name
        if _help: params['help'] = _help

        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def get_computer_contracts(self,computer_id,id2name=None,_help=None):
        """
        Return a JSON serialized list of computer contracts from the
        GLPI server.

        :type computer_id: integer
        :type id2name: boolean
        :type _help: boolean
        :param computer_id: ID of the computer
        :param id2name: associate labels with IDs and return with the rest of the JSON result
        :param _help: return JSON serialized information about this API call
        """

        params = {'method':'glpi.getComputerContracts',
                  'session':self.session}
        if id2name: params['id2name'] = id2name
        if _help: params['help'] = _help

        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def get_network_equipment(self,network_equipment_id,id2name=None,infocoms=None,
                              contracts=None,networkports=None,_help=None):
        """
        Return a JSON serialized network object from the GLPI
        server.

        :type network_equipment_id: integer
        :type id2name: boolean
        :type infocoms: boolean
        :type contracts: boolean
        :type networkports: boolean
        :type _help: boolean
        :param network_equipment_id: ID of the network equipment
        :param id2name: associate labels with IDs and return with the rest of the JSON result
        :param infocoms: return infocoms associated with the network equipment
        :param contracts: return contracts associated with the network equipment
        :param networkports: return information about the equipments network ports
        :param _help: return JSON serialized information about this API call
        """
        params = {'method':'glpi.getNetworkEquipment',
                  'session':self.session,
                  'id':network_equipment_id}

        if id2name: params['id2name'] = id2name
        if infocoms: params['infocoms'] = infocoms
        if contracts: params['contracts'] = contracts
        if networkports: params['networkports'] = networkports
        if _help: params['help'] = _help

        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def get_infocoms(self,_id,itemtype,id2name=None,_help=None):
        """
        Return a JSON serialized list of computer's financial
        information from the GLPI server.

        :type _id: integer
        :type itemtype: integer
        :type id2name: boolean
        :type _help: boolean
        :param _id: object id
        :param itemtype: the object type
        :param id2name: option to enable id to name translation of dropdown fields
        :param _help: Get help from the server
        """
        params = {'method':'glpi.getInfoComs',
                  'session':self.session,
                  #'id':infocoms_id,
                  'itemtype':itemtype}
        if id2name: params['id2name'] = id2name
        if _help: params['help'] = _help
        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def get_contracts(self,_id,id2name=None,_help=None):
        """
        Return a JSON serialized list of contracts from the GLPI server.

        :type _id: integer
        :type id2name: boolean
        :type _help: boolean
        :param _id: computer id
        :param id2name: option to enable id to name translation of dropdown fields
        :param _help: get help from server
        """
        params = {'method':'glpi.getContracts',
                  'session':self.session,
                  'id':_id}
        if id2name: params['id2name'] = id2name
        if _help: params['help'] = _help

        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def get_network_ports(self,_id,itemtype,id2name=None,_help=None):
        """
        Return a JSON serialized list of network ports from the GLPI
        server.

        :type _id: integer
        :type itemtype: string
        :type id2name: boolean
        :type _help: boolean
        :param _id: object ID
        :param itemtype: values can be:
          - Computer
          - Peripheral
          - NetworkEquipment
          - Phone
          - Printer
        :param id2name: option to enable id to name translation of dropdown fields
        :param _help: get help from server about this api call
        """

        params = {'method':'glpi.getNetworkports',
                  'session':self.session,
                  'id':_id,
                  'itemtype':itemtype}

        if id2name: params['id2name'] = id2name
        if _help: params['help'] = _help

        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())


    def list_computers(self,count=None,_help=None):
        """
        Return a JSON serialized list of computers from the GLPI
        server.

        :type count: list
        :type _help: boolean
        :param count: iterable containing start and limit integers
        :param _help: get help from server about this API call
        """
        params = {'method':'glpi.listComputers',
                  'session':self.session}
        if count:
            if len(count) < 2:
                raise Exception("List needs to include a start and limit integer")
            if len(count) == 2:
                params['start'] = count[0]
                params['limit'] = count[1]
        if _help: params['help'] = _help
        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def list_dropdown_values(self,dropdown,_id=None,parent=None,name=None,
                             helpdesk=None,criteria=None,count=None,_help=None):
        """
        Return a list of dropdown menus from the GLPI server.

        :type dropdown: string
        :type _id: integer
        :type name: string
        :type helpdesk: string
        :type criteria: string
        :type count: list
        :type _help: boolean

        :param dropdown: name of the dropdown, must be a GLPI class. Special dropdowns are:

          - ticketstatus
          - ticketurgency
          - ticketimpact
          - tickettype
          - ticketpriority
          - ticketglobalvalidation
          - ticketvalidationstatus

        :param _id: id of the entry
        :param name: optional string (mysql % joker allowed)
        :param helpdesk: filter on 'is_helpdeskvisible' attribute (TicketCategory) (deprecated, use criteria=helpdesk intead)
        :param criteria: filter on a boolean attribute (is_xxx)
        :param count: iterable containing start and limit integers
        :param _help: get usage information
        """
        params = {'method':'glpi.listDropdownValues',
                  'session':self.session,
                  'dropdown':dropdown}
        if _id: params['id'] = _id
        if parent: params['parent'] = parent
        if name: params['name'] = name
        if helpdesk: params['helpdesk'] = helpdesk
        if criteria: params['criteria'] = criteria
        if count:
            if len(count) < 2:
                raise Exception("List needs to include a start and limit integer")
            if len(count) == 2:
                params['start'] = count[0]
                params['limit'] = count[1]
        if _help: params['help'] = _help
        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def list_groups(self,mine=None,parent=None,under=None,withparent=None,filter=None,
                    count=None,_help=None):
        """
        Return a JSON serialized list of groups from the GLPI server.

        :type mine: boolean
        :type parent: integer
        :type under: integer
        :type withparent: boolean
        :type filter: string
        :type count: list
        :type _help: boolean

        :param mine: only retrieve groups of connected user
        :param parent: only retrieve groups under selected parent (group ID)
        :param under: only retrive child groups of selected one (group ID)
        :param withparent: also search for recursive group in parent's entities
        :param filter: filter, options include:

          - is_requester
          - is_assign
          - is_notify
          - is_itemgroup
          - is_usergroup

        :param count: iterable containing start and limit integers
        :param _help: get usage information
        """
        params = {'method':'glpi.listGroups',
                  'session':self.session}
        if mine: params['mine'] = mine
        if parent: params['parent'] = parent
        if under: params['under'] = under
        if withparent: params['withparent'] = withparent
        if filter: params['filter'] = filter
        if count:
            if len(count) < 2:
                raise Exception("List needs to include a start and limit integer")
            if len(count) == 2:
                params['start'] = count[0]
                params['limit'] = count[1]
        if _help: params['help'] = _help
        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def list_helpdesk_items(self,itemtype,id2name=None,count=None,_help=None):
        """
        Return a JSON serialized list of helpdesk items from the GLPI
        server.

        :type itemtype: string
        :type id2name: boolean
        :type count: list
        :type _help: boolean
        :param itemtype: list *allowed* items for the authenticated user to open a helpdesk ticket on, can be:

          - my: returns all my devices
          - empty: returns general helpdesk items

        :param id2name: option to enable id to name translation of dropdown menus
        :param count: iterable containing start and limit integers
        :param _help: option to get usage information
        """
        params = {'method':'glpi.listHelpdeskItems',
                  'session':self.session,
                  'itemtype':itemtype}

        if id2name: params['id2name'] = id2name
        if count:
            if len(count) < 2:
                raise Exception("List needs to include a start and limit integer")
            if len(count) == 2:
                params['start'] = count[0]
                params['limit'] = count[1]
        if _help: params['help'] = _help

        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def list_helpdesk_types(self,count=None,_help=None):
        """
        Return a JSON serialized list of helpdesk types from the GLPI
        server.

        :type count: list
        :type _help: boolean
        :param count: iterable containing start and limit integers
        :param _help: get usage information
        """

        params = {'method':'glpi.listHelpdeskTypes',
                  'session':self.session}
        if count:
            if len(count) < 2:
                raise Exception("List needs to include a start and limit integer")
            if len(count) == 2:
                params['start'] = count[0]
                params['limit'] = count[1]
        if _help: params['help'] = _help

        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def list_inventory_objects(self,count=None,_help=None):
        """
        Return a JSON serialized list of inventory objects from the
        GLPI server.

        User must be a super admin to use this method.

        :type count: list
        :type _help: boolean
        :param count: list including start and limit
        :param _help: get usage information
        """
        params = {'method':'glpi.listInventoryObjects',
                  'session':self.session}
        if count:
            if len(count) < 2:
                raise Exception("List needs to include a start and limit integer")
            if len(count) == 2:
                params['start'] = count[0]
                params['limit'] = count[1]
        if _help: params['help'] = _help
        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def list_objects(self, itemtype, location_name=None,
                     locations_id=None, name=None, otherserial=None,
                     room=None, building=None, serial=None,
                     show_label=None, count=None, _help=None):
        """
        Return as list of objects from the GLPI server.

        User must be a super admin to use this method.

        :type itemtype: string
        :type location_name: string
        :type locations_id: integer
        :type name: string
        :type otherserial: string
        :type room: string
        :type building: string
        :type serial: string
        :type show_label: boolean
        :type count: list
        :type _help: boolean
        :param itemtype: **required** itemtypes are plentiful and `available here <https://forge.indepnet.net/embedded/glpi/hierarchy.html>`_
        :param location_name:
        :param locations_id:
        :param name:
        :param otherserial:
        :param room:
        :param building:
        :param serial:
        :param show_label:
        :param count: list including start and limit
        :param _help: get usage information

        .. note:: link in itemtypes param is a of all GLPI classes, some are not retrievable through webservices.
        """
        params = {'method':'glpi.listObjects',
                  'session':self.session,
                  'itemtype':itemtype}
        if location_name: params['location_name'] = location_name
        if locations_id: params['location_id'] = locations_id
        if name: params['name'] = name
        if otherserial: params['otherserial'] = otherserial
        if room: params['room'] = room
        if building: params['building'] = building
        if serial: params['serial'] = serial
        if show_label: params['show_label'] = show_label

        if count:
            if len(count) < 2:
                raise Exception("List needs to include a start and limit integer")
            if len(count) == 2:
                params['start'] = count[0]
                params['limit'] = count[1]
        if _help: params['help'] = _help
        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def list_tickets(self,mine=None,user=None, recipient=None,
                     group=None, mygroups=None, category=None,
                     status=None, startdate=None, enddate=None,
                     itemtype=None, item=None, entity=None,
                     satisfaction=None, approval=None, approver=None,
                     order=None, id2name=None, count=None,
                     _help=None):
        """
        Return a JSON serialized list of tickets from the GLPI server.

        :type mine: bool
        :type user: int
        :type recipient: int
        :type group: int
        :type mygroups: bool
        :type category: int
        :type status: string
        :type startdate: datetime
        :type enddate: datetime
        :type itemtype: string
        :type item: int
        :type entity: int
        :type satisfaction: int
        :type approval: string
        :type approver: int
        :type order: list
        :type count: list
        :type id2name: bool
        :type _help: bool
        :param mine: list tickets of user B{or} recipient
        :param user: ID of the victim: person concerned by the ticket
        :param recipient: ID of the requestor: person who created the ticket
        :param group: ID of the requestor group (must have show_all_ticket or show_group_ticket right)
        :param mygroups: list of groups of current user
        :param category: ID of the category of the ticket
        :param status: status of the ticket, must be:

          - notold
          - old
          - process
          - waiting
          - old_done
          - new
          - old_notdone
          - assign
          - plan
          - all

        :param startdate: start of the period where the ticket is active (close date after this)
        :param enddate: end of the period where the ticket is active (open date before this)
        :param itemtype: ID of the type of the item (see L{GLPIClient.list_helpdesk_types})
        :param item: ID of the item, requires itemtype
        :param entity: ID of the entity of the ticket
        :param satisfaction: only closed tickets with a satisfaction survey:

          0. all
          1. waiting
          2. answered

        :param approval: only tickets with a validation request:

          - all
          - waiting
          - accepted
          - pending

        :param approver: user ID, only tickets with a validation request sent to this user
        :param order: list of allowed key names:

          - id
          - date
          - closedate
          - date_mod
          - status
          - users_id
          - groups_id
          - entities_id
          - priority

        :param id2name: option to enable id to name translation of dropdown menus
        :param count: iterable including start and limit integers
        :param _help: get usage information
        """
        params = {'method':'glpi.listTickets',
                  'session':self.session}
        if mine: params['mine'] = mine
        if user: params['user'] = user
        if recipient: params['recipient'] = recipient
        if group: params['group'] = group
        if mygroups: params['mygroups'] = mygroups
        if category: params['category'] = category
        if status: params['status'] = status
        if startdate: params['startdate'] = startdate
        if enddate: params['enddate'] = enddate
        if itemtype: params['itemtype'] = itemtype
        if item: params['item'] = item
        if entity: params['entity'] = entity
        if satisfaction: params['satisfaction'] = satisfaction
        if approval: params['approval'] = approval
        if approver: params['approver'] = approver
        if order: params['order'] = order
        if id2name: params['id2name'] = id2name
        if count:
            if len(count) < 2:
                raise Exception("List needs to include a start and limit integer")
            if len(count) == 2:
                params['start'] = count[0]
                params['limit'] = count[1]
        if _help: params['help'] = _help
        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def list_users(self, user=None, group=None, location=None,
                   login=None, name=None, entity=None, parent=None,
                   order=None, count=None, _help=None):
        """
        Return a JSON serialized list of users from the GLPI server.

        :type user: int
        :type group: int
        :type location: int
        :type login: string
        :type name: string
        :type entity: int
        :type parent: bool
        :type order: list
        :type count: list
        :type _help: bool
        :param user: ID of user, returns single user
        :param group: ID of group
        :param location: ID of location
        :param login: login name (mysql % joker allowed)
        :param name: name (mysql % joker allowed)
        :param entity: ID of entity
        :param parent: search or not for user with recursive right on parent entities (default: True)
        :param order: order of the result, must be one or more of the following,:

          - id
          - name
          - login

        :param count: iterable including start and limit integers
        :param _help: get usage information

        .. note:: order defaults to 'id'
        """

        params = {'method':'glpi.listUsers',
                  'session':self.session}
        if user: params['user'] = user
        if group: params['group'] = group
        if location: params['location'] = location
        if login: params['login'] = login
        if name: params['name'] = name
        if entity: params['entity'] = entity
        if parent: params['parent'] = parent
        if order: params['order'] = order
        if count:
            if len(count) < 2:
                raise Exception("List needs to include a start and limit integer")
            if len(count) == 2:
                params['start'] = count[0]
                params['limit'] = count[1]
        if _help: params['help'] = _help

        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    """
    Action methods
    """

    def create_ticket(self,title,content,entity=None,user=None,group=None,requester=None,
                      victim=None,observer=None,date=None,itemtype=None,item=None,
                      urgency=None,_type=None,source=None,category=None,user_email=None,
                      user_email_notification=None,_help=None):
        """
        Returns a JSON serialized version of a ticket upon
        success. Unless otherwise noted, all params are optional

        :type entity: integer
        :type user: integer or list of integers
        :type group: integer or list of integers
        :type requester: integer or list of integers
        :type victim: integer or list of integers
        :type observer: integer or list of integers
        :type date: ISO formatted date string
        :type itemtype: integer
        :type item: integer
        :type title: string
        :type content: string
        :type urgency: integer
        :type _type: integer
        :type source: string
        :type category: integer
        :type user_email: string
        :type user_email_notification: boolean
        :type _help: boolean
        :param entity: ID, optional, default is current on, must be in the active ones
        :param user: requester ID, default to current logged in user
        :param group: requester ID, default is None
        :param requester: additional requester(s) with mail notification
        :param victim: same as requester, without mail notification
        :param observer: additional observers
        :param date: defaults to system date
        :param itemtype: id of the type of the item, optional, default none
        :param item: ID of the item, optional, default none
        :param title: **required** short description of the issue
        :param content: **required** longer description of the issue
        :param urgency: defaults to 3, 1-5 are accepted
        :param _type: type of ticket, defaults to 1
        :param source: name of the RequestType, optional, defaults WebServices
        :param category: default is none
        :param user_email: enable notification to this email address
        :param user_email_notification: enable notification to the users email (if known)
        :param _help: list available options in JSON
        """

        params = {'method':'glpi.createTicket',
                  'session':self.session,
                  'title':title,
                  'content':content}
        if entity: params['entity'] = entity
        if user: params['user'] = user
        if group: params['group'] = group
        if requester: params['requester'] = requester
        if victim: params['victim'] = victim
        if observer: params['observer'] = observer
        if date: params['date'] = date
        if itemtype: params['itemtype'] = itemtype
        if item: params['item'] = item
        if urgency: params['urgency'] = urgency
        if _type: params['type'] = _type
        if source: params['source'] = source
        if category: params['category'] = category
        if user_email: params['user_email'] = user_email
        if user_email_notification: params['user_email_notification'] = user_email_notification
        if help: params['help'] = _help

        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def add_ticket_document(self, ticket, url=None, name=None,
                            base64=None, comment=None, content=None,
                            _help=None):
        """
        Add a document to an existing ticket if the authenticated user can edit it.

        .. note:: base64 and url are mutually exclusive.

        Returns the ticket if the call succeeds.

        :type ticket: integer
        :type url: string
        :type name: string
        :type base64: base64 encoded string
        :type comment: string
        :type content: string
        :type help: boolean
        :param ticket: ID of the ticket
        :param url: url of the document to be uploaded
        :param name: name of the document
        :param base64: content of the document in base64 encoded string
        :param comment: depracated, use *content* instead
        :param content: if present, also add a followup, if the
          documentation upload succeeded, for additional options, see
          `GLPIClient.add_ticket_followup`
        :param help: get usage information
        """
        params = {'method':'glpi.createTicket',
                  'session':self.session,
                  'ticket':ticket}
        if url: params['url'] = url
        if name: params['name'] = name
        if base64: params['base64'] = base64
        if comment: params['comment'] = comment
        if content: params['content'] = content
        if _help: params['help'] = _help
        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def add_ticket_followup(self, ticket, content, source=None,
                            private=None, reopen=None, close=None,
                            _help=None):
        """
        Add a followup to an existing ticket if the authenticated user
        can edit it.

        Returns a hashtable of the modified ticket object (See L{GLPIClient.get_ticket}).

        :type ticket: integer
        :type content: string
        :type source: string
        :type private: boolean
        :type reopen: boolean
        :type close: boolean
        :type _help: boolean

        :param ticket: ID of the ticket
        :param content: B{required} content of the new followup
        :param source: name of the RequestType (created if needed), defaults to 'WebServices'
        :param private: mark followup as private, defaults to 0
        :param reopen: set ticket to working state (deny solution for 'solved' ticket or answer for 'waiting' ticket)
        :param close: close a 'solved' ticket
        :param _help: get usage information
        """
        params = {'method':'glpi.createTicket',
                  'session':self.session,
                  'ticket':ticket,
                  'content':content}

        if source: params['source'] = source
        if private: params['private'] = private
        if reopen: params['reopen'] = reopen
        if close: params['close'] = close
        if _help: params['help'] = _help
        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def add_ticket_observer(self, ticket, user=None, _help=None):
        """
        Add a new observer to an existing ticket.

        Current user can add himself to a ticket he can view.

        Other users can be added if allowed to update the ticket.

        Returns a JSON serialized ticket upon success (as in
        L{GLPIClient.get_ticket})

        :type ticket: integer
        :type user: integer
        :param ticket: ID of the ticket
        :param user: ID of the user

        """
        params = {'method':'glpi.createTicket',
                  'session':self.session,
                  'ticket':ticket}
        if user: params['user'] = user
        if _help: params['help'] = _help
        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def set_ticket_satisfaction(self, ticket, satisfaction,
                                comment=None, _help=None):
        """
        Answer to the ticket satisfaction survey

        Returns a JSON serialized ticket (See L{GLPIClient.get_ticket})

        :type ticket: integer
        :type satisfaction: integer
        :type comment: string
        :type _help: boolean

        :param ticket: ID of ticket
        :param satisfaction: ID of the satisfaction answer, 0-5
        :param comment: optional comment
        :param _help: get usage information
        """
        params = {'method':'glpi.createTicket',
                  'session':self.session,
                  'ticket':ticket,
                  'satisfaction':satisfaction}
        if comment: params['comment'] = comment
        if _help: params['help'] = _help
        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def set_ticket_validation(self, approval, status, comment=None,
                              _help=None):

        """
        Answer to the ticket approval request.

        Returns a JSON serialized ticket upon success (See L{GLPIClient.get_ticket}).

        :type approval: integer
        :type status: string
        :type comment: string
        :type _help: boolean
        :param approval: ID of the request
        :param status: request status, can be:
          - waiting
          - rejected
          - accepted
        :param comment: optional string, *required* if status is 'rejected'
        :param _help: get usage information
        """
        params = {'method':'glpi.createTicket',
                  'session':self.session,
                  'approval':approval,
                  'status':status}
        if comment: params['comment'] = comment
        if _help: params['help'] = _help
        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def create_objects(self,fields,_help=None):
        """
        Create new objects

        User must be super admin to run this method.

        Returns a newly created JSON serialized object upon success.

        :type fields: list
        :type _help: boolean
        :param fields: inject data into GLPI
        :param _help: get usage information
        """
        params = {'method':'glpi.createTicket',
                  'session':self.session,
                  'fields':fields}
        if _help: params['help'] = _help

        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def delete_objects(self,fields,_help=None):
        """
        Delete or purge objects from GLPI.

        User must be super admin to run this method.

         @type fields: dict
         @param fields: dict of fields to delete
         Example from deleteObjects doc:
             https://forge.indepnet.net/projects/webservices/wiki/GlpideleteObjects:

             fields = {
                 'Computer': {
                     27: 1,
                     28: 0,
                 },
                 'Monitor': {
                     5: 1,
                     6: 1,
                 }
             }

         @return: a list of deleted fields
        """
        params = {
                'method':'glpi.deleteObjects',
                'session':self.session,
        }
        for type in fields:
            for id in fields[type]:
                params['fields[%s][%s]' % (type, id)] = fields[type][id]
        if _help: params['help'] = _help

        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def update_objects(self,fields,_help=None):
        """
        Update existing objects in GLPI.

        User must be super admin to run this method.

        TODO: What does this thing return?

        """
        params = {'method':'glpi.createTicket',
                  'session':self.session,
                  'fields':fields}
        if _help: params['help'] = _help

        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

    def link_objects(self,fields,_help):
        """
        Link an object to another object (when it is impossible with L{GLPIClient.create_objects}).

        User must be super admin to run this method.

        TODO: What does this thing return?
        """
        params = {'method':'glpi.createTicket',
                  'session':self.session,
                  'fields':fields}
        if _help: params['help'] = _help

        response = urllib2.urlopen(self.__request__(params))
        return json.loads(response.read())

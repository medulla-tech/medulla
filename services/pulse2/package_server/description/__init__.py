#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id$
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
# ma 02110-1301, USA.

"""
    Pulse2 PackageServer
"""
from twisted.web import resource
import logging
import cgi

class Description(resource.Resource):
    type = 'Description'
    isLeaf = True
    def __init__(self, services, status = {}):
        self.services = services
        self.status = status
        resource.Resource.__init__(self)
        self.logger = logging.getLogger()
        self.logger.info("(%s) initialised with : %s"%(self.type, self.services))

    def __up(self):
        return "<td class='up mandriva'>&nbsp;&nbsp;</td>"

    def __down(self):
        return "<td class='down mandriva'>&nbsp;&nbsp;</td>"

    def render_GET(self, request):
        serverdetail = {}
        #if request.path != '/':
        #    return ''

        body = "<html>"
        body += "<table class='mandriva'>"
        body += "<tr class='mandriva'><th class='mandriva'>URL</th><th class='mandriva'>Kind</th><th class='mandriva'>Details</th><th class='mandriva'>State</th></tr>"
        for description in self.services:
            style = ''
            if request.args.has_key('server') and request.args['server'] == description['server'] and \
                    request.args.has_key('port') and int(request.args['port']) == int(description['port']) and \
                    request.args.has_key('proto') and request.args['proto'] == description['proto'] and \
                    request.args.has_key('mp') and request.args['mp'] == description['mp'] and \
                    request.args.has_key('type') and request.args['type'] == description['type']:
                style = 'selected'

            body += "<tr class='mandriva "+style+"'><td class='mandriva "+style+"'>"+description['proto']+"://"+description['server']+":"+str(description['port'])+description['mp']+"</td><td class='mandriva "+style+"'>"+description['type']+"</td>"
            try:
                if description['type'] == 'mirror_files':
                    if not self.status[description['mp']]:
                        body += "<td class='mandriva "+style+"'>content</td>"
                        body += self.__down()
                    else:
                        url = "?uri="+description['proto']+"://"+description['server']+":"+str(description['port'])+cgi.escape(description['mp'])+"&proto="+description['proto']+"&server="+description['server']+"&port="+str(description['port'])+"&mp="+cgi.escape(description['mp'])+"&type="+description['type']
                        serverdetail[description['server']+':'+str(description['port'])+description['mp']] = url
                        body += "<td class='mandriva "+style+"'><a class='mandriva "+style+"' href=\""+url+"\">content</a></td>"
                        body += self.__up()
                else:
                    # FIXME NR/MDV : are the four lines below useful ?
                    # print '%s://%s:%s%s'%(description['proto'], description['server'], str(description['port']), description['mp'])
                    # import xmlrpclib
                    # client = xmlrpclib.ServerProxy('%s://%s:%s%s'%(description['proto'], description['server'], str(description['port']), description['mp']))
                    # ret = client.getServerDetails()
                    url = "?proto="+description['proto']+"&server="+description['server']+"&port="+str(description['port'])+"&mp="+cgi.escape(description['mp'])+"&type="+description['type']
                    serverdetail[description['server']+':'+str(description['port'])+description['mp']] = url
                    body += "<td class='mandriva "+style+"'><a class='mandriva "+style+"' href='"+url+"'>details</a></td>"
                    body += self.__up()
                    self.status[description['mp']] = True
            except Exception:
                body += "<td class='mandriva "+style+"'>details</td>"
                body += self.__down()
                self.status[description['mp']] = False
            body += "</tr>"
        body += "</table>"
        body += "<hr class='mandriva'/>"

#        if request.args['uri'] then
#            body += "<iframe class='mandriva' style='width:100%; heigth:100%;' src=#{request.args['uri']}>Your browser don't support iframes</iframe>"
#        elsif request.args['add_package'].to_s == 1.to_s then
#            body += "<form class='mandriva'>"
#            body += "<table class='mandriva'>"
#            body += "<tr class='mandriva'><td class='mandriva'>id</td><td class='mandriva'><input type='text' name='id' id='id'></input></td></tr>"
#            body += "<tr class='mandriva'><td class='mandriva'>label</td><td class='mandriva'><input type='text' name='name' id='name'></input></td></tr>"
#            body += "<tr class='mandriva'><td class='mandriva'>description</td><td class='mandriva'><input type='text' name='description' id='description'></input></td></tr>"
#            body += "<tr class='mandriva'><td class='mandriva'>textual version</td><td class='mandriva'><input type='text' name='version' id='version'></input></td></tr>"
#            body += "<tr class='mandriva'><td class='mandriva'>numerical version</td><td class='mandriva'><input type='text' name='nversion' id='nversion'></input></td></tr>"
#            body += "<tr class='mandriva'><td class='mandriva'>command</td><td class='mandriva'><input type='text' name='cmd' id='cmd'></input></td></tr>"
#            body += "<tr class='mandriva'><td class='mandriva' colspan='2'><button class='mandriva' name='save'/>Save</td></tr>"
#            body += "</table>"
#            body += "<input type='hidden' name='add_package' id='add_package' value='2'/>"
#            body += "<input type='hidden' name='proto' id='proto' value='#{request.args['proto']}'/>"
#            body += "<input type='hidden' name='server' id='server' value='#{request.args['server']}'/>"
#            body += "<input type='hidden' name='port' id='port' value='#{request.args['port']}'/>"
#            body += "<input type='hidden' name='mp' id='mp' value='#{request.args['mp']}'/>"
#            body += "</form>"
#        elsif request.args['add_package'].to_s == 2.to_s then
#            label = request.args['name']
#            id = request.args['id']
#            version = request.args['version']
#            nversion = request.args['nversion']
#            desc = request.args['description']
#            cmd = Mandriva::Command.new('CMD', request.args['cmd'])
#            pack = Mandriva::Package.new().init(id, label, version, 0, desc, cmd)
#
#            body += "will try to connect to : #{request.args['server']}:#{request.args['port']}/#{request.args['mp']}"
#            begin
#                server = connect(request.args['server'], request.args['port'], request.args['mp'])
#                pid, path = server.call('xmlrpc.putPackageDetail', pack.toH)
#
#                if not pid then
#                    body += " --> failed"
#                else
#                    body += " --> done<br/>"
#                    body += "please copy your files in #{path} on server #{request.args['server']}"
#                end
#            rescue
#                body += " --> failed"
#            end
#        elsif request.args['server'] then
#            begin
#                body += "<table class='mandriva'>"
#                server = connect(request.args['server'], request.args['port'], request.args['mp'])
#                server.timeout = 5
#                ret = server.call('xmlrpc.getServerDetails')
#                case request.args['type']
#                when 'package_api_put'
#                    body += "<tr class='mandriva'><th class='mandriva'>Label</th><th class='mandriva'>Version</th><th class='mandriva'>Size</th></tr>"
#                    url = serverdetail[request.args['server']+':'+request.args['port']+request.args['mp']]
#                    ret.each do |papi|
#                        style = ''
#                        if papi['id'] == request.args['package'] then
#                            style = 'selected'
#                        end
#                        body += "<tr class='mandriva #{style}'><td class='mandriva #{style}'><a href='#{url}&package=#{papi['id']}' class='mandriva #{style}'>#{papi['label']}</a></td><td class='mandriva #{style}'>#{papi['version']}</td><td class='mandriva #{style}'>#{humanSize(papi['size'])}</td></tr>"
#                    end
#                    body += "<tr class='mandriva'><td colspan='3'><a href='#{url}&add_package=1' class='mandriva fontblack'>add a new package</a></td></tr>"
#                when 'package_api_get', 'mirror'
#                    body += "<tr class='mandriva'><th class='mandriva'>Label</th><th class='mandriva'>Version</th><th class='mandriva'>Size</th></tr>"
#                    url = serverdetail[request.args['server']+':'+request.args['port']+request.args['mp']]
#                    ret.each do |papi|
#                        style = ''
#                        if papi['id'] == request.args['package'] then
#                            style = 'selected'
#                        end
#                        body += "<tr class='mandriva #{style}'><td class='mandriva #{style}'><a href='#{url}&package=#{papi['id']}' class='mandriva #{style}'>#{papi['label']}</a></td><td class='mandriva #{style}'>#{papi['version']}</td><td class='mandriva #{style}'>#{humanSize(papi['size'])}</td></tr>"
#                    end
#                when 'mirror_api'
#                    if not ret['package_api_get'].nil?
#                        body += "<tr class='mandriva'><td class='mandriva'><h3 class='mandriva'>Package API GET</h3></td></tr>"
#                        ret['package_api_get'].each do |papi|
#                            style = ''
#                            body += "<tr class='mandriva #{style}'><td class='mandriva #{style}'>#{papi['protocol']}://#{papi['server']}:#{papi['port']}#{papi['mountpoint']}</td></tr>"
#                        end
#                    end
#                    if not ret['package_api_put'].nil?
#                        body += "<tr class='mandriva'><td class='mandriva'><h3 class='mandriva'>Package API PUT</h3></td></tr>"
#                        ret['package_api_put'].each do |papi|
#                            style = ''
#                            body += "<tr class='mandriva #{style}'><td class='mandriva #{style}'>#{papi['protocol']}://#{papi['server']}:#{papi['port']}#{papi['mountpoint']}</td></tr>"
#                        end
#                    end
#                    if not ret['mirror'].nil?
#                        body += "<tr class='mandriva'><td class='mandriva'><h3 class='mandriva'>Mirrors</h3></td></tr>"
#                        ret['mirror'].each do |m|
#                            body += "<tr class='mandriva'><td class='mandriva'>#{m['protocol']}://#{m['server']}:#{m['port']}#{m['mountpoint']}</td></tr>"
#                        end
#                    end
#                end
#                body += "</table>"
#            rescue XMLRPC::FaultException => e
#                body += "<span class='mandriva error'><pre class='mandriva'>#{cgi::escapeHTML(e.faultString)}</pre></span>"
#            rescue Exception => e
#                body += "<span class='mandriva error'><pre class='mandriva'>#{cgi::escapeHTML(e.inspect)}</pre></span>"
#            end
#        end
#
#        if request.args['package'] then
#            body += "<hr class='mandriva'/>"
#            pkg = Mandriva::Common.instance.packages(request.args['mp'])[request.args['package']]
#            body += "<table class='mandriva'>"
#            body += "<tr class='mandriva'><th class='mandriva'>Type</th><th class='mandriva'>Commands</th></tr>"
#            body += "<tr class='mandriva'><td class='mandriva'>Pre command</td><td class='mandriva'>#{pkg.precmd.to_s}</td></tr>"
#            body += "<tr class='mandriva'><td class='mandriva'>Initialisation command</td><td class='mandriva'>#{pkg.initcmd.to_s}</td></tr>"
#            body += "<tr class='mandriva'><td class='mandriva'>Command</td><td class='mandriva'>#{pkg.cmd.to_s}</td></tr>"
#            body += "<tr class='mandriva'><td class='mandriva'>Failure post command</td><td class='mandriva'>#{pkg.postcmd_ko.to_s}</td></tr>"
#            body += "<tr class='mandriva'><td class='mandriva'>Success post command</td><td class='mandriva'>#{pkg.postcmd_ok.to_s}</td></tr>"
#            body += "</table>"
#
#            body += "<br/>"
#            body += "<table class='mandriva'>"
#            body += "<tr class='mandriva'><th class='mandriva'>Id</th><th class='mandriva'>File</th>"
#            if request.args['type'] != 'package_api_get'
#                body += "<th class='mandriva'>Uri</th>"
#            end
#            body += "<th class='mandriva'>Size</th></tr>"
#            pkg.files.each do |file|
#                body += "<tr class='mandriva'><td class='mandriva'>#{file.id}</td><td class='mandriva'>#{file.to_s}</td>"
#                if request.args['type'] != 'package_api_get'
#                    body += "<td class='mandriva'><a href='#{file.toURI}' class='mandriva fontblack'>#{file.toURI}</a></td>"
#                end
#                body += "<td class='mandriva'>#{humanSize(file.size)}</td></tr>"
#            end
#            body += "</table>"
#        end

        body += "<style>"
        body += ".fontblack {"
        body += "    color: black !important;"
        body += "}"
        body += ".selected {"
        body += "    background-color: #999999 !important;"
        body += "    color: black !important;"
        body += "}"
        body += ".error {"
        body += "    color:red;"
        body += "}"
        body += "table.mandriva {"
        body += "    background-color: #ccccd7;"
        body += "}"
        body += "tr.mandriva {"
        body += "}"
        body += "th.mandriva, h3.mandriva {"
        body += "    padding-left: 15px;"
        body += "    padding-right: 15px;"
        body += "    background-color: #9AA6C4;"
        body += "}"
        body += "td.mandriva {"
        body += "    padding-left: 15px;"
        body += "    padding-right: 15px;"
        body += "    background-color: #dddde8;"
        body += "}"
        body += "a.mandriva:link {"
        body += "    color: grey;"
        body += "}"
        body += "a.mandriva:visited {"
        body += "    color: grey;"
        body += "}"
        body += "a.mandriva {"
        body += "    text-decoration: none;"
        body += "    color: grey;"
        body += "}"
        body += ".up {"
        body += "    background-color: #00cc00 !important;"
        body += "}"
        body += ".down {"
        body += "    background-color: #cc0000 !important;"
        body += "}"
        body += ".ukn {"
        body += "    background-color: #CCCCCC !important;"
        body += "}"
        body += "</style>"
        body += "</html>"

        return body



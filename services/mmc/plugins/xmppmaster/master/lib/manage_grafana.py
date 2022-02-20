#!/usr/bin/python3
# -*- coding: utf-8; -*-
#
# (c) 2020 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
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
#
# file: lib/manage_grafana.py

import os
import logging
import ConfigParser
import json
import requests
import socket

logger = logging.getLogger()


class manage_grafana:
    """
    This class provides the functions needed to create/edit/delete Grafana
    panels via the API
    It uses the configuration stored in grafana_api section of the file
    /etc/mmc/plugins/xmppmaster.ini
    """

    def __init__(self, hostname, configfilepath=None):
        self.hostname = hostname
        self.api_config = {}

        if configfilepath is None:
            self.configfile = "/etc/mmc/plugins/xmppmaster.ini"
        else:
            self.configfile = configfilepath
        if os.path.exists(self.configfile):
            self.configuration()
        else:
            # No config file found
            logger.error("/etc/mmc/plugins/xmppmaster.ini not found.")

    def configuration(self):
        """
        Reads the configuration from ini and ini.local files
        """
        config = ConfigParser.ConfigParser()
        config.readfp(open(self.configfile))
        if os.path.isfile(self.configfile + ".local"):
            config.readfp(open(self.configfile + ".local", "r"))

        if config.has_option("grafana_api", "api_key"):
            self.api_config["api_key"] = config.get("grafana_api", "api_key")
        else:
            logger.error(
                "API Key is not defined. " "Please define it in xmppmaster.ini.local"
            )
            return
        if config.has_option("grafana_api", "url"):
            self.api_config["url"] = config.get("grafana_api", "url")
        else:
            self.api_config["url"] = "http://localhost:3000"
        if config.has_option("grafana_api", "render_url"):
            self.api_config["render_url"] = config.get("grafana_api", "render_url")
        else:
            self.api_config["render_url"] = (
                "http://%s/grafana/render/d-solo" % socket.getfqdn()
            )
        if config.has_option("grafana_api", "graph_url"):
            self.api_config["graph_url"] = config.get("grafana_api", "graph_url")
        else:
            self.api_config["graph_url"] = "http://%s/grafana/d-solo" % socket.getfqdn()

        logger.debug("API configuration: %s" % self.api_config)
        return

    def grafanaGetDashboardForHostname(self):
        """Returns a JSON containing the dashboard for a hostname"""
        # Check all parameters and prepare request
        try:
            logger.debug("Getting dashboard for hostname %s" % self.hostname)
            headers = {"Authorization": "Bearer %s" % self.api_config["api_key"]}
            url = "%s/api/dashboards/uid/%s" % (self.api_config["url"], self.hostname)
        except KeyError:
            logger.error("API key or url is not defined")
            return None
        # Send request to grafana API
        try:
            r = requests.get(url, headers=headers)
            if r.status_code != requests.codes.ok:
                logger.error("Error getting dashboard for hostname %s" % self.hostname)
                logger.error("Received status code %s" % r.status_code)
                logger.error("Complete response: %s" % r.text)
                return None
            # Dashboard found. Return the dashboard's JSON
            logger.debug("JSON dashboard response: %s" % json.dumps(r.json(), indent=4))
            return r.json()
        except requests.RequestException as e:
            logger.error(
                "Error getting dashboard for hostname %s: %s" % (self.hostname, str(e))
            )
            return None

    def grafanaGetDashboardIdForHostname(self):
        try:
            logger.debug("Getting dashboard id for hostname %s" % self.hostname)
            db_json = self.grafanaGetDashboardForHostname()
            logger.debug(
                "dashboard id for hostname %s: %s"
                % (self.hostname, db_json["dashboard"]["id"])
            )
            return db_json["dashboard"]["id"]
        except Exception as e:
            logger.error(
                "Error getting dashboard id for hostname%s: %s"
                % (self.hostname, str(e))
            )
            return None

    def grafanaWriteDashboardForHostname(self, dashb_json):
        """Writes the JSON containing the dashboard"""
        # Check all parameters and prepare request
        try:
            logger.info("Creating dashboard for hostname %s" % self.hostname)
            headers = {"Authorization": "Bearer %s" % self.api_config["api_key"]}
            url = "%s/api/dashboards/db" % self.api_config["url"]
        except KeyError:
            logger.error("API key or url is not defined")
            return None
        # Send request to grafana API
        try:
            r = requests.post(url, headers=headers, json=dashb_json)
            if r.status_code != requests.codes.ok:
                logger.error("Error writing dashboard for hostname %s" % self.hostname)
                logger.error("Received status code %s" % r.status_code)
                logger.error("Complete response: %s" % r.text)
                return None
            # Dashboard written successfully. Return dashboard id
            logger.debug("JSON dashboard response: %s" % json.dumps(r.json(), indent=4))
            return r.json()["id"]
        except requests.RequestException as e:
            logger.error(
                "Error writing dashboard for hostname %s: %s" % (self.hostname, str(e))
            )
            return None

    def grafanaCreateDashboard(self):
        # Prepare payload
        payload = {}
        dashboard = {}
        dashboard["uid"] = self.hostname
        dashboard["title"] = self.hostname
        dashboard["timezone"] = "utc"
        dashboard["time"] = {}
        dashboard["time"]["from"] = "now/d"
        dashboard["time"]["to"] = "now/d"
        dashboard["panels"] = []
        payload["dashboard"] = dashboard
        payload["folderId"] = 0
        payload["overwrite"] = False
        dashb_id = self.grafanaWriteDashboardForHostname(payload)
        if dashb_id:
            logger.info(
                "Dashboard %s created for hostname %s" % (dashb_id, self.hostname)
            )
            return dashb_id
        # Error writing dashboard
        logger.error("Error creating dashboard for hostname %s" % self.hostname)
        return None

    def grafanaGetPanels(self):
        """Returns a JSON containing the panels for a hostname"""
        try:
            logger.debug("Getting panels for hostname %s" % self.hostname)
            db_json = self.grafanaGetDashboardForHostname()
            panel_json = []
            for panel in db_json["dashboard"]["panels"]:
                panel_json.append({"id": panel["id"], "title": panel["title"]})
            logger.debug(
                "dashboard panels for hostname %s: %s" % (self.hostname, panel_json)
            )
            return panel_json
        except Exception:
            logger.warning("No panels defined for hostname %s" % self.hostname)
            return None

    def grafanaGetPanelIdFromTitle(self, panel_title):
        try:
            logger.debug(
                "Getting panel %s id for hostname %s" % (panel_title, self.hostname)
            )
            current_panels = self.grafanaGetPanels()
            for index, panel in enumerate(current_panels):
                if panel_title == panel["title"]:
                    logger.debug(
                        "Panel %s has id %s and index %s"
                        % (panel_title, panel["id"], index)
                    )
                    return panel["id"]
            logger.debug(
                "Panel %s not found for hostname %s" % (panel_title, self.hostname)
            )
            return None
        except Exception as e:
            logger.error(
                "Error while getting panel %s for hostname %s: %s"
                % (panel_title, self.hostname, str(e))
            )
            return None

    def grafanaEditPanel(self, panel_json):
        """Add or edit a panel to the dashboard from the JSON contents"""
        panel_dict = json.loads(panel_json)
        # Check if dashboard exists. If not create it
        db_id = self.grafanaGetDashboardIdForHostname()
        if not db_id:
            db_id = self.grafanaCreateDashboard()
        if db_id is None:
            logger.error("Error getting panel for hostname %s" % self.hostname)
            return None
        # Get current dashboard and add panel if it does not exist
        # If it exists, update the panel
        current_panels = self.grafanaGetPanels()
        db_json = self.grafanaGetDashboardForHostname()
        try:
            for index, panel in enumerate(current_panels):
                if panel_dict["title"] == panel["title"]:
                    panel_id = panel["id"]
                    panel_index = index
        except Exception:
            logger.debug("No panels found for hostname %s" % self.hostname)
        # if panel_id and panel_index are defined, delete the panel
        try:
            logger.info("Updating panel %s for hostname %s" % (panel_id, self.hostname))
            # Remove existing panel
            db_json["dashboard"]["panels"].remove(panel_index)
        except NameError:
            try:
                panel_id = max(current_panels, key=lambda x: x["id"])["id"] + 1
            except (TypeError, ValueError):
                panel_id = 1
                logger.info(
                    "Adding panel %s for hostname %s" % (panel_id, self.hostname)
                )
        # Insert id and add the panel to dashboard json
        panel_dict["id"] = int(panel_id)
        db_json["dashboard"]["panels"].append(panel_dict)
        logger.debug(
            "New dashboard json for hostname %s: %s" % (self.hostname, db_json)
        )
        dashb_id = self.grafanaWriteDashboardForHostname(db_json)
        if dashb_id:
            logger.info(
                "Dashboard %s updated with panel %s "
                "for hostname %s" % (dashb_id, panel_dict["title"], self.hostname)
            )
            return True
        # Error writing dashboard
        logger.error(
            "Error writing panel %s to dashboard "
            "for hostname %s" % (panel_dict["title"], self.hostname)
        )
        return False

    def grafanaDeleteDashboard(self):
        # Check all parameters and prepare request
        try:
            logger.info("Deleting dashboard for hostname %s" % self.hostname)
            headers = {"Authorization": "Bearer %s" % self.api_config["api_key"]}
            url = "%s/api/dashboards/uid/%s" % (self.api_config["url"], self.hostname)
        except KeyError:
            logger.error("API key or url is not defined")
            return None
        # Send request to grafana API
        try:
            r = requests.delete(url, headers=headers)
            if r.status_code != requests.codes.ok:
                logger.error("Error deleting dashboard for hostname %s" % self.hostname)
                logger.error("Received status code %s" % r.status_code)
                logger.error("Complete response: %s" % r.text)
                return None
            logger.debug("JSON dashboard response: %s" % json.dumps(r.json(), indent=4))
            return r.json()
        except requests.RequestException as e:
            logger.error(
                "Error deleting dashboard for hostname %s: %s" % (self.hostname, str(e))
            )
            return None

    def grafanaDeletePanel(self, panel_title):
        # Get dashboard for hostname and delete the panel
        logger.info("Deleting panel %s for hostname %s" % (panel_title, self.hostname))
        db_json = self.grafanaGetDashboardForHostname()
        for index, panel in enumerate(db_json["dashboard"]["panels"]):
            if panel["title"] == panel_title:
                panel_index = index
        if panel_index:
            db_json["dashboard"]["panels"].remove(panel_index)
            logger.debug(
                "New dashboard json for hostname %s: %s" % (self.hostname, db_json)
            )
            dashb_id = self.grafanaWriteDashboardForHostname(db_json)
            if dashb_id:
                logger.info(
                    "Panel %s deleted from dashboard %s "
                    "for hostname %s" % (panel_title, dashb_id, self.hostname)
                )
                return True
            # Error writing dashboard
            logger.error(
                "Error deleting panel %s from dashboard "
                "for hostname %s" % (panel_title, self.hostname)
            )
            return False
        # No panel found
        logger.error(
            "Error deleting panel %s from dashboard "
            "for hostname %s: Pannel not found" % (panel_title, self.hostname)
        )
        return False

    def grafanaGetPanelImage(self, panel_title, from_timestamp, to_timestamp):
        """Returns the url of the image generated by Grafana for a panel"""
        logger.debug(
            "Getting image url for panel %s for hostname %s"
            % (panel_title, self.hostname)
        )
        panel_id = self.grafanaGetPanelIdFromTitle(panel_title)
        if panel_id:
            img = "%s/%s/%s?panelId=%s&width=800&height=400&from=%s&to=%s" % (
                self.api_config["render_url"],
                self.hostname,
                self.hostname,
                panel_id,
                from_timestamp * 1000,
                to_timestamp * 1000,
            )
            logger.debug(
                "Image url for panel %s for hostname %s: %s"
                % (panel_title, self.hostname, img)
            )
            return img
        # No panel found
        return None

    def grafanaGetPanelGraph(self, panel_title, from_timestamp, to_timestamp):
        """Returns the url of the page generated by Grafana for a panel"""
        logger.debug(
            "Getting graph url for panel %s for hostname %s"
            % (panel_title, self.hostname)
        )
        panel_id = self.grafanaGetPanelIdFromTitle(panel_title)
        if panel_id:
            graph_page = "%s/%s/%s?panelId=%s&width=800&height=400&from=%s&to=%s" % (
                self.api_config["graph_url"],
                self.hostname,
                self.hostname,
                panel_id,
                from_timestamp * 1000,
                to_timestamp * 1000,
            )
            logger.debug(
                "Graph url for panel %s for hostname %s: %s"
                % (panel_title, self.hostname, graph_page)
            )
            return graph_page
        # No panel found
        return None

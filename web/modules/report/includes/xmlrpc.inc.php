<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
/*
 * Get all available reports
 */

function getAllReports() {
    return xmlCall("report.getAllReports");
}

/*
 * Method to get a report result.
 * Give plugin, report_name, method to call,
 * optionaly args and kargs for this method
 *
 * @param $plugin: mmc plugin name (aka pkgs, imaging, glpi, ...)
 * @type $plugin: str
 * @param report_name: report class name
 * @type report_name: str
 * @param method: report class method to be called
 * @type method: str
 *
 * @return: report method result
 */

function get_report_datas($plugin, $report_name, $method, $args = array(), $kargs = array()) {
    return xmlCall("report.get_report_datas", array($plugin, $report_name, $method, array($args, $kargs)));
}

function get_xls_report($reports) {
    return xmlCall("report.get_xls_report", array($reports));
}

function get_pdf_report($reports) {
    return xmlCall("report.get_pdf_report", array($reports));
}

function get_svg_file($report) {
    return xmlCall("report.get_svg_file", array($report));
}

function get_report_sections($lang) {
    return xmlCall("report.get_report_sections", array($lang));
}

function generate_report($period, $sections, $entities, $lang) {
    return xmlCall("report.generate_report", array($period, $sections, $entities, $lang));
}

?>

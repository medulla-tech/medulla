<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2013 Mandriva, http://www.mandriva.com
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

require_once("modules/report/includes/xmlrpc.inc.php");
require_once("modules/report/includes/html.inc.php");
require_once("modules/pulse2/includes/utilities.php");

function parseReports($f) {
    foreach(getAllReports() as $plugin => $reports) {
        $f->push(new Div());

        foreach($reports as $report) {
            $report_path = implode('/', $report);
            try {
                $include_path = "modules/$plugin/report/$report_path.php";
                if (! @include_once($include_path))
                    throw new Exception("$include_path does not exists");
            }
            catch (Exception $e){
                $f->add(new TitleElement(_T('WARNING missing file: ', 'report')));
                $f->add(new textTpl($e->getMessage()));
            }
            print '<br />';
        }
        $f->pop();
    }
}

// New validating form
$f = new ValidatingForm();

/*
 * $_SESSION['report_files']
 * Used to store datas for PDF/XLS reports
 * $_SESSION['report_files'][mmc_plugin_name][report_name]
 */

if (!isset($_SESSION['report_files'])) $_SESSION['report_files'] = array();

// first step, display selectors
if (!array_intersect_key($_POST, array('display_results' => '', 'get_xls' => '', 'get_pdf' => ''))) {
    // Push a table
    $f->push(new Table());

    /*
     * Period
     */

    $f->add(
        new TrFormElement(_T('Period:','report'), new periodInputTpl(_T('from', 'report'), 'period_from', _T('to', 'report'), 'period_to')),
        array("value" => $values,"required" => True)
    );

    /*
     * Entities
     */
    $entities = new SelectItem('entities');
    list($list, $values) = getEntitiesSelectableElements();
    $entities->setElements($list);
    $entities->setElementsVal($values);
    //$entities->setSelected($selected);

    $f->add(
        new TrFormElement(_T('Entities', 'report'), $entities),
        array()
    );

    // close the table
    $f->pop();
}

// Parse reports
parseReports($f);

// A <br /> to add space up to validate buttons
$f->push(new Div());
$f->add(new SpanElement('<br />'));
$f->pop();

if (!array_intersect_key($_POST, array('display_results' => '', 'get_xls' => '', 'get_pdf' => ''))) {
    $f->addButton("display_results", _T('Display Report', 'report'));
}
// second step, display results
elseif (isset($_POST['display_results'])) {
    $f->addButton("get_xls", _T("Get XLS Report", "report"));
    $f->addButton("get_pdf", _T("Get PDF Report", "report"));
}
// third step, get xls or pdf report
else {
    if (isset($_POST['get_xls']))
        header("Location: " . urlStrRedirect("report/report/get_file", array('type' => 'xls')));
    elseif(isset($_POST['get_pdf']))
        header("Location: " . urlStrRedirect("report/report/get_file", array('type' => 'pdf')));
}
$f->display();
?>

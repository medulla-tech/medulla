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


$modules = get_report_sections($_SESSION['lang']);

#print '<pre>';
#print_r($modules);
#print '</pre>';
// New validating form
$f = new ValidatingForm();

/*
 * $_SESSION['report_files']
 * Used to store datas for PDF/XLS reports
 * $_SESSION['report_files'][mmc_plugin_name][report_name]
 */

if (!isset($_SESSION['report_files']))
    $_SESSION['report_files'] = array();

// first step, display selectors
if (!array_intersect_key($_POST, array('generate_report' => '', 'get_xls' => '', 'get_pdf' => ''))) {
    // Push a table
    $f->push(new Table());

    /*
     * Period
     */

    $f->add(
            new TrFormElement(_T('Period:', 'report'), new periodInputTpl(_T('from', 'report'), 'period_from', _T('to', 'report'), 'period_to')), array("value" => $values, "required" => True)
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
            new TrFormElement(_T('Entities', 'report'), $entities), array()
    );

    // close the table
    $f->pop();

    foreach ($modules as $module_name => $sections) {
        $f->add(new TitleElement($module_name));
        $f->push(new Table());
        foreach ($sections as $section) {
            $f->add(new TrFormElement(
                    $section['title'], new ValueCheckboxTpl("selected_sections[]")), array("value" => $section['name'])
            );
        }
        $f->pop();
    }
}

// A <br /> to add space up to validate buttons
$f->push(new Div());
$f->add(new SpanElement('<br />'));
$f->pop();

if (!array_intersect_key($_POST, array('generate_report' => '', 'get_xls' => '', 'get_pdf' => ''))) {
    $f->addButton("generate_report", _T('Generate Report', 'report'));
}
// second step, display results
elseif (isset($_POST['generate_report'])) {
    print '<pre>';
    print_r($_POST['selected_sections']);
    print '</pre>';

    $ts_from = intval($_POST['period_from_timestamp']);
    $ts_to = intval($_POST['period_to_timestamp']);

    $nb_days = intval(($ts_to - $ts_from) / 86400);
    $nb_periods = max($nb_days, 7);

    $periods = array();

    for ($i = 0; $i < $nb_days; $i++) {
        $period_ts = $ts_from + $i * ($ts_to - $ts_from) / ($nb_days - 1);
        $periods[] = strftime('%Y-%m-%d', $period_ts);
    }

    $result = generate_report($periods, $_POST['selected_sections'], array($_POST['entities']), $_SESSION['lang']);


    printf('<a class="btnPrimary" href="%s">%s</a>', urlStrRedirect("report/report/get_file", array('path' => $result['xls_path'])), _T("Get XLS Report", "report"));
    printf('<a class="btnPrimary" href="%s">%s</a>', urlStrRedirect("report/report/get_file", array('path' => $result['pdf_path'])), _T("Get PDF Report", "report"));
}

$f->display();
?>

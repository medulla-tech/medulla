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
require_once("modules/report/includes/report.inc.php");
require_once("modules/pulse2/includes/utilities.php");

$MMCApp =& MMCApp::getInstance();
$report = get_report_sections($_SESSION['lang']);

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
        new TrFormElement(_T('Entities', 'report'), $entities),
        array());

    foreach($report as $module_name => $sections) {
        $moduleObj = $MMCApp->getModule($module_name);
        $f->add(
            new TrFormElement($moduleObj->getDescription(),
                              new ReportModule($module_name, $sections)),
            array());
    }

    $f->pop();
}

// A <br /> to add space up to validate buttons
$f->push(new Div());
$f->add(new SpanElement('<br />'));
$f->pop();

if (!array_intersect_key($_POST, array('generate_report' => '', 'get_xls' => '', 'get_pdf' => ''))) {
    $f->addButton("generate_report", _T('Generate Report', 'report'));
}
// second step, display results
else if (isset($_POST['generate_report'])) {
    $ts_from = intval($_POST['period_from_timestamp']);
    $ts_to = intval($_POST['period_to_timestamp']) + 86400;

    $nb_days = intval(($ts_to - $ts_from) / 86400);
    $nb_periods = min($nb_days, 7);

    $periods = array();

    for ($i = 0; $i < $nb_periods; $i++) {
        $period_ts = $ts_from + $i * ($ts_to - $ts_from) / ($nb_periods - 1);
        $periods[] = strftime('%Y-%m-%d', $period_ts);
    }

    $items = array();
    foreach($_POST['indicators'] as $name => $status) {
        $items[] = $name;
    }
    $sections = array();
    foreach($_POST['sections'] as $section) {
        if ($section)
            $sections[] = $section;
    }

    $result = generate_report($periods, $sections, $items, array($_POST['entities']), $_SESSION['lang']);
    // display sections

    foreach ($result['sections'] as $section) {
        // Section Title
        $f->push(new Div());
        $title = new TitleElement($section['title']);
        $f->add($title);
        $f->pop();

        // Display tables and graphs for this section
        $report_objects = array();
        $report_types = array();
        foreach ($section['content'] as $content) {
            $table = False;
            $svg = False;
            if ($content['type'] == 'table') {
                $title = new SpanElement(sprintf('<h3>%s</h3>', $content['title']));
                $report_objects[] = $title;
                $report_types[] = 'title';

                if (in_array('titles', array_keys($content['data']))) {
                    // period table
                    $titles = $content['data']['titles'];
                    $values = $content['data']['values'];
                    $dates = $content['data']['dates'];
                    $table = new OptimizedListInfos($titles, "");
                    for ($i = 0; $i < count($dates); $i++) {
                        $table->addExtraInfo($values[$i], $dates[$i]);
                    }

                    if ($table) {
                        $table->setNavBar(new AjaxNavBar($itemCount, $filter));
                    }
                } elseif (in_array('headers', array_keys($content['data']))) {
                    // key_value table
                    $headers = $content['data']['headers'];
                    $values = $content['data']['values'];

                    for ($i = 0; $i < count($headers); $i++) {
                        $tab_values = array();
                        foreach ($values as $value) {
                            $tab_values[] = $value[$i];
                        }
                        if (!$table) {
                            $table = new ListInfos($tab_values, $headers[$i]);
                        } else {
                            $table->addExtraInfo($tab_values, $headers[$i]);
                        }
                    }
                }
            } elseif ($content['type'] == 'chart') {
                $filename = $content['svg_path'];
                $handle = fopen($filename, 'r');
                $svg_content = fread($handle, filesize($filename));
                fclose($handle);
                $svg = new SpanElement(sprintf('<div align="center">%s<br /><a align="center" class="btn" href="%s">%s</a></div>', $svg_content, urlStrRedirect("report/report/get_file", array('path' => $content['png_path'])), _T('Download image', 'report')));
            }
            if ($table) {
                $report_objects[] = $table;
                $report_types[] = 'table';
            }
            if ($svg) {
                $report_objects[] = $svg;
                $report_types[] = 'svg';
            }
        }

        // report_objects and report_types are collected
        // Now if there is any chart, put it right of table
        for ($i = 0; $i < count($report_types); $i++) {
            $f->push(new Div());
            if ($report_types[$i] == 'table' && $report_types[$i + 1] == 'svg') {
                $f->add((new multicol())
                                ->add($report_objects[$i], '60%', '0 2% 0 0')
                                ->add($report_objects[$i + 1], '40%')
                );
                $i++;
            } else {
                $f->add($report_objects[$i]);
            }
            $f->pop();
        }
    }


    $f->push(new Div());
    $link = new SpanElement(sprintf('<br /><a class="btnPrimary" href="%s">%s</a>&nbsp;&nbsp;', urlStrRedirect("report/report/get_file", array('path' => $result['xls_path'])), _T("Get XLS Report", "report")));
    $f->add($link);
    $link = new SpanElement(sprintf('<a class="btnPrimary" href="%s">%s</a>', urlStrRedirect("report/report/get_file", array('path' => $result['pdf_path'])), _T("Get PDF Report", "report")));
    $f->add($link);
    $f->pop();
}

$f->display();

?>

<style>
    .report-indicator label {
        display: inline !important;
    }
</style>

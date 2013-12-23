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
?>

<script type="text/javascript" src="modules/report/lib/pygal/svg.jquery.js"></script>
<script type="text/javascript" src="modules/report/lib/pygal/pygal-tooltips.js"></script>

<?php
require("graph/navbar.inc.php");
require_once("modules/report/includes/xmlrpc.inc.php");
require_once("modules/report/includes/html.inc.php");
require_once("modules/report/includes/report.inc.php");
require_once("modules/pulse2/includes/utilities.php");

$MMCApp =& MMCApp::getInstance();
$report = get_report_sections($_SESSION['lang']);

$t = new TitleElement(_T("Report creation", 'report'));
$t->display();

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
    $f->push(new Table());
    /* Period */
    $f->add(
        new TrFormElement(_T('Period', 'report'),
                          new periodInputTpl(_T('from', 'report'), 'period_from', _T('to', 'report'), 'period_to')),
        array("value" => $values, "required" => True)
    );
    /* Entities */
    $entities = new SelectMultiTpl('entities[]');
    list($list, $values) = getEntitiesSelectableElements();
    $entities->setElements($list);
    $entities->setElementsVal($values);
    if (count($list) > 15)
        $entities->setHeight(15);
    else
        $entities->setFullHeight();
    $f->add(
        new TrFormElement(_T('Entities', 'report'), $entities),
        array("required" => true));
    /* Modules indicators */
    foreach($report as $module_name => $sections) {
        $moduleObj = $MMCApp->getModule($module_name);
        if ($moduleObj) {
            $f->add(
                new TrFormElement($moduleObj->getDescription(),
                                  new ReportModule($module_name, $sections)),
                array());
        }
    }

    $f->pop();
    $f->addButton("generate_report", _T('Generate Report', 'report'));
}
// second step, display results
else if (isset($_POST['generate_report'])) {
    $ts_from = intval($_POST['period_from_timestamp']);
    $ts_to = intval($_POST['period_to_timestamp']);

    $datediff = $ts_to + 86400 - $ts_from;
    $nb_days = floor($datediff/(60*60*24));

    $nb_periods = min($nb_days, 7);

    $interval = ($nb_days > 7) ? $nb_days / 7 : 1;

    $periods = array(date('Y-m-d', $ts_from));

    for ($i = 1; $i < ($nb_periods - 1); $i++) {
        $periods[] = date('Y-m-d', strtotime("+" . round($interval * $i) . " days", $ts_from));
    }
    $periods[] = date('Y-m-d', $ts_to);

    $items = array();
    foreach($_POST['indicators'] as $name => $status) {
        $items[] = $name;
    }
    $sections = array();
    foreach($_POST['sections'] as $section) {
        if ($section)
            $sections[] = $section;
    }
    $entities = array();
    foreach($_POST['entities'] as $uuid) {
        if ($uuid)
            $entities[] = $uuid;
    }

    if (empty($items)) {
        new NotifyWidgetFailure(_T("Select some data to include in the report.", "report"));
        redirectTo(urlStrRedirect("report/report/index"));
    }

    $result = generate_report($periods, $sections, $items, $entities, $_SESSION['lang']);

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
                    $table = new ListInfos($titles, "");
                    for ($i = 0; $i < count($dates); $i++) {
                        $table->addExtraInfo($values[$i], $dates[$i]);
                    }
                    $table->end = count($titles);
                }
                else if (in_array('headers', array_keys($content['data']))) {
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
            }
            else if ($content['type'] == 'chart') {
                $filename = $content['svg_path'];
                $handle = fopen($filename, 'r');
                $svg_content = fread($handle, filesize($filename));
                fclose($handle);
                $svg = new SpanElement(sprintf('<div align="center">%s<br /><a align="center" class="btn" href="%s">%s</a></div>',
                                       $svg_content,
                                       urlStrRedirect("report/report/get_file", array('path' => $content['png_path'])),
                                       _T('Download image', 'report')));
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
            if (count($report_objects[$i]->arrInfo) > 0) {
                $f->push(new Div());
                if ($report_types[$i] == 'table' && $report_types[$i + 1] == 'svg') {
                    $f->add((new multicol())
                                    ->add($report_objects[$i], '60%', '0 2% 0 0')
                                    ->add($report_objects[$i + 1], '40%')
                                );
                    $i++;
                }
                else {
                    $f->add($report_objects[$i]);
                }
                if ($report_types[$i] != 'title')
                    $f->add(new SpanElement('<br /><hr style="border-top: 1px solid #DDDDDD"/><br />'));
                $f->pop();
            }
            else {
                $f->add($report_objects[$i]);
            }
        }
    }


    $f->push(new Div());
    $link = new SpanElement(sprintf('<br /><a class="btn btn-primary" href="%s">%s</a>&nbsp;&nbsp;', urlStrRedirect("report/report/get_file", array('path' => $result['xls_path'])), _T("Get XLS Report", "report")));
    $f->add($link);
    $link = new SpanElement(sprintf('<a class="btn btn-primary" href="%s">%s</a>', urlStrRedirect("report/report/get_file", array('path' => $result['pdf_path'])), _T("Get PDF Report", "report")));
    $f->add($link);
    $f->pop();
}

$f->display();

?>

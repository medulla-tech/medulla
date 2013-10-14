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

/*
 * This file is included in report main page
 * You have access to $f variable
 */

// Current Report title

$f->push(new Div());
$title = new TitleElement(_T("Monitoring", "report"));
$f->add($title);
$f->pop();

// first step, display selectors
if (!array_intersect_key($_POST, array('display_results' => '', 'get_xls' => '', 'get_pdf' => ''))) {
    $f->push(new Table());
    $f->add(new TrFormElement(
        _T('Disc Space', 'report'), 
        new CheckboxTpl("disc_space")), array("value" => False ? "checked" : "")
    );
    $f->add(new TrFormElement(
        _T('RAM', 'report'), 
        new CheckboxTpl("ram")), array("value" => False ? "checked" : "")
    );
    $f->pop();
}
// second step, display results
elseif (isset($_POST['display_results'])) {
    /*
     * get disc space datas
     * We send:
     *      from_timestamp
     *      to_timestamp
     *      splitter (split period into X parts)
     */
    
    if ($_POST['disc_space']) {
        /*
         * Title
         */
        
        $f->push(new Div());
        $title = new TitleElement(_T("Disc Space", "report"));
        $f->add($title);
        $f->pop();

        /*
         * Table
         */

        $args = array(
            $_POST['period_from_timestamp'],
            $_POST['period_to_timestamp'],
            7,
        );
        $_SESSION['report_files']['report']['Monitoring - Disc Space'] = array('report', 'Monitoring.Monitoring', 'get_disc_space', $args);
        $values = get_report_datas('report', 'Monitoring.Monitoring', 'get_disc_space', $args);
        ksort($values);

        $table = null;
        foreach ($values as $k => $v) {
            if ($table == null) {
                $table = new OptimizedListInfos($v, "");
            }
            else {
                $table->addExtraInfo($v, timestamp_to_date($k));
            }
        }

        if ($table) {
            $table->setNavBar(new AjaxNavBar($itemCount, $filter));
        }

        /*
         * SVG
         */
        
        $span = new ReportSVG('disc_space', array('report', 'Monitoring.Monitoring', 'get_disc_space_svg', $args));

        $f->add((new multicol())
            ->add($table, '60%', '0 2% 0 0')
            ->add($span, '40%')
        );
    }
    else {
        if (isset($_SESSION['report_files']['report']['Monitoring - Disc Space']))
            unset($_SESSION['report_files']['report']['Monitoring - Disc Space']);
    }

    if ($_POST['ram']) {
        /*
         * get ram usage
         * We send:
         *      from_timestamp
         *      to_timestamp
         *      splitter (split period into X parts)
         */

        /*
         * Title
         */

        $f->push(new Div());
        $title = new TitleElement(_T("Ram Usage", "report"));
        $f->add($title);
        $f->pop();

        /*
         * Table
         */
        
        $args = array(
            $_POST['period_from_timestamp'],
            $_POST['period_to_timestamp'],
            7,
        );
        $_SESSION['report_files']['report']['Monitoring - Ram Usage'] = array('report', 'Monitoring.Monitoring', 'get_ram_usage', $args);
        $values = get_report_datas('report', 'Monitoring.Monitoring', 'get_ram_usage', $args);
        ksort($values);
        $table = null;
        $f->push(new Div());
        foreach ($values as $k => $v) {
            if ($table == null) {
                $table = new OptimizedListInfos($v, "");
            }
            else {
                $table->addExtraInfo($v, timestamp_to_date($k));
            }
        }

        if ($table) {
            $table->setNavBar(new AjaxNavBar($itemCount, $filter));
        }
        $f->add($table);
        $f->pop();
    }
    else {
        if (isset($_SESSION['report_files']['report']['Monitoring - Ram Usage']))
            unset($_SESSION['report_files']['report']['Monitoring - Ram Usage']);
    }
}
// third step, get xls or pdf report, nothing to do here
else {
}

?>

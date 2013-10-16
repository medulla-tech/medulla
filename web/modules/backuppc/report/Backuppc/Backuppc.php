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
$title = new TitleElement(_T("Backuppc", "report"));
$f->add($title);
$f->pop();

// first step, display selectors
if (!array_intersect_key($_POST, array('display_results' => '', 'get_xls' => '', 'get_pdf' => ''))) {
    $f->push(new Table());

    /*
     * BackupPC Server Used Disc space indicator
     */

    $f->add(new TrFormElement(
        _T('BackupPC Server Used Disc Space', 'report'), 
        new CheckboxTpl("backuppc_server_disc_space")), array("value" => False ? "checked" : "")
    );

    /*
     * Used Disc Space Per Machine indicator
     */

    $f->add(new TrFormElement(
        _T('Used Disc Space Per Machine', 'report'), 
        new CheckboxTpl("backuppc_disc_space_per_machine")), array("value" => False ? "checked" : "")
    );

    $f->pop();

    /*
     * If indicator is checked, div below is showed to ask for some values
     */

    $div = new Div(
        array(
            'id' => 'backuppc_disc_space_per_machine_div',
        )
    );
    $div->setVisibility(False); // Hidden by default ;-)

    $f->push($div);
    $f->push(new Table());

    // Title and description
    $section_title = _T('Used Disc Space Per Machine', 'report');
    $section_desc = _T('Display only machines where critical Disc Space Limit is reached except if "Display All Machines" is checked', 'report');
    $span = new SpanElement(sprintf('<h3>%s</h3><p>%s</p>', $section_title, $section_desc));
    $f->add(new TrFormElement("", $span), array());

    $f->add(
        new TrFormElement(
            _T('Display All Machines', 'report'), 
            new CheckboxTpl("backuppc_used_disc_space_all_machines"),
            array("value" => False ? "checked" : "")
        )
    );

    // Input field
    $input = new InputTpl('backuppc_critical_limit');

    // Select field
    $select = new SelectItem('backuppc_critical_limit_unit');
    $critical_limit_unit = array(
        "Mo",
        "Go",
    );
    $select->setElements($critical_limit_unit);
    $select->setElementsVal($critical_limit_unit);
    $select->setSelected('Go');

    $tr = new TrFormElement(
            _T('Critical Disc Space Limit', 'report'), 
            (new multicol())
                ->add($input, '10%', 0, array('value' => 10))
                ->add($select, '90%')
        );
    $tr->setClass('backuppc_critical_space_limit_class');
    $f->add(
        $tr
    );

    $f->pop(); // pop table
    $f->pop(); // pop div
}
// second step, display results
elseif (isset($_POST['display_results'])) {
    if ($_POST['backuppc_server_disc_space']) {
        /*
         * Title
         */
        
        $f->push(new Div());
        $title = new TitleElement(_T("BackupPC Server Disc Space", "report"));
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

        $kargs = array('entities' => $_POST['entities']);

        $_SESSION['report_files']['backuppc']['BackupPC Server Disc Space'] = array('backuppc', 'Backuppc.Backuppc', 'get_backuppc_server_disc_space', $args, $kargs);
        $result = get_report_datas('backuppc', 'Backuppc.Backuppc', 'get_backuppc_server_disc_space', $args, $kargs);

        foreach ($result as $entity_id => $values) {
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

            $kargs = array(
                'entities' => $entity_id,
            );
            $span = new ReportSVG('backuppc_server_disc_space', array('backuppc', 'Backuppc.Backuppc', 'get_backuppc_server_disc_space_svg', $args, $kargs));

            $f->add((new multicol())
                ->add($table, '60%', '0 2% 0 0')
                ->add($span, '40%')
            );
        }
    }
    else {
        if (isset($_SESSION['report_files']['backuppc']['BackupPC Server Disc Space']))
            unset($_SESSION['report_files']['backuppc']['BackupPC Server Disc Space']);
    }
    if ($_POST['backuppc_disc_space_per_machine']) {
        /*
         * Title
         */
        
        $f->push(new Div());
        $title = new TitleElement(_T("Used Disc Space Per Machine", "report"));
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

        $kargs = array(
            'entities' => $_POST['entities'],
            'display_all_machines' => (isset($_POST['backuppc_used_disc_space_all_machines'])) ? True : False,
            'critical_limit' => $_POST['backuppc_critical_limit'],
            'critical_limit_unit' => $_POST['backuppc_critical_limit_unit'],
        );

        $_SESSION['report_files']['backuppc']['Used Disc Space Per Machine'] = array('backuppc', 'Backuppc.Backuppc', 'get_backuppc_used_disc_space_per_machine', $args, $kargs);
        $result = get_report_datas('backuppc', 'Backuppc.Backuppc', 'get_backuppc_used_disc_space_per_machine', $args, $kargs);

        foreach ($result as $entity_id => $values) {
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

            $kargs['entities'] = $entity_id;
            $span = new ReportSVG('backuppc_disc_space_per_machine', array('backuppc', 'Backuppc.Backuppc', 'get_backuppc_used_disc_space_per_machine_svg', $args, $kargs));

            $f->add((new multicol())
                ->add($table, '60%', '0 2% 0 0')
                ->add($span, '40%')
            );
        }
    }
    else {
        if (isset($_SESSION['report_files']['backuppc']['Used Disc Space Per Machine']))
            unset($_SESSION['report_files']['backuppc']['Used Disc Space Per Machine']);
    }

}
// third step, get xls or pdf report, nothing to do here
else {
}

?>
<script type='text/javascript'>
jQuery(function() {
    // If "Used Disc Space Per Machine" is checked, show the indicator's section
    jQuery('#backuppc_disc_space_per_machine').click(function() {
        if(jQuery('#backuppc_disc_space_per_machine').is(':checked')) {
            jQuery('#backuppc_disc_space_per_machine_div').show('slow');
        }
        else {
            jQuery('#backuppc_disc_space_per_machine_div').hide('slow');
        }
    });

    // If "Display All Machines" is checked, hide "Critical Disc Space Limit" input field
    jQuery('#backuppc_used_disc_space_all_machines').click(function() {
        if(jQuery('#backuppc_used_disc_space_all_machines').is(':checked')) {
            jQuery('.backuppc_critical_space_limit_class').hide('slow');
        }
        else {
            jQuery('.backuppc_critical_space_limit_class').show('slow');
        }
    });
});
</script>

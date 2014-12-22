<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
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

include_once("modules/dashboard/includes/panel.class.php");
require_once("modules/update/includes/xmlrpc.inc.php");

$options = array(
    "class" => "ClientUpdatePanel",
    "id" => "updateclient",
    "refresh" => 14400,
    "title" => _("Clients Update"),
    "enable" => TRUE
);

class ClientUpdatePanel extends Panel {

    function display_content() {
        $updates = get_updates(array('filters'=>array('status'=>0)))[data];
        $update_count = count($updates);
        if ($updates === FALSE){

        // Update error occured
        printf('<center style="color:red;font-weight:bold">%s</center>', _T('An error occured while fetching updates'));
        } else {

            $view_updates_text = _T('View updates', 'update');

            print '<center>';

            if ($update_count == 0)
                printf('<p><strong>%s</strong></p>', _T('No updates available.', 'update'));
            else{
                printf('<p><strong>%d %s</strong></p>', $update_count, _T('updates available.', 'update'));

                print <<<EOS
                <a title="View updates" class="btnSecondary"
                    href="main.php?module=update&amp;submod=update&amp;action=index"
                    >$view_updates_text</a><br/><br/>
EOS;
            }
        }
        $machine_update_status=get_machines_update_status();
        $statut_count=array_count_values($machine_update_status);
        $state_name = array(
            "up-to-date"=>_T("Up-to-date"),
            "update_available"=>_T("Updates availables"),
            "unknown"=>_T("Not registered"),
        );
        $state_color = array(
            "up-to-date"=>'000-#73d216-#42780D',
            "update_available"=>'000-#ef2929-#A31A1A',
            "unknown"=>'000-#000000-#666665',
        );
        $urlRedirect = urlStrRedirect("base/computers/createUpdateStaticGroup");
        foreach ($statut_count as $status => $count) {
            $data[]=$count;
            $label[]=$state_name[$status].' (' . $count . ')';
            $colors[]=$state_color[$status];
            $links[]=$urlRedirect."&status=".$status;
        }
        $data=json_encode($data);
        $label=json_encode($label);
        $colors=json_encode($colors);
        $links=json_encode($links);
        $createGroupText = json_encode(_T("Create a group", "update"));
        print <<<CHART
        <div id="update_status"></div>
        <script type="text/javascript">
        var r = Raphael("update_status"),
                radius = 70,
                margin = 40,
                x = 100,
                y = 75;
        var data = $data,
            colors = $colors,
            legend = $label,
            href = $links,
            title = 'Update Status';
        percentdata = getPercentageData(data);
        pie = r.piechart(x, y + 5, radius, percentdata,
                       {colors: colors})
         .hover(function () {
            this.sector.stop();
            this.sector.animate({ transform: 's1.1 1.1 ' + this.cx + ' ' + this.cy }, 800, "elastic");

            if (this.label) {
                this.label[0].stop();
                this.label[0].attr({ r: 7.5 });
                this.label[1].attr({ "font-weight": 800 });
            }
         }, function () {
            this.sector.animate({ transform: 's1 1 ' + this.cx + ' ' + this.cy }, 800, "elastic");

            if (this.label) {
                this.label[0].animate({ r: 5 }, 500, "bounce");
                this.label[1].attr({ "font-weight": 400 });
            }
         });

        y += (radius * 2) + margin + 5;

        r.setSize(200, (radius * 1 + margin) + 50);
        // Legend
        jQuery('#update_status').append('<ul></ul>');
        for (var i = 0; i < legend.length; i++) {
            jQuery('#update_status ul').append(
                '<li style="color: ' + colors[i].split('-')[1]  + ';"><span style="color: #000">' + legend[i]
                + '<a href="' + href[i] + '"><img title="' + $createGroupText +
                '" style="height: 10px; padding-left: 3px;" src="img/machines/icn_machinesList.gif" /></a></span></li>'
            );
        }
        </script>
        <style type="text/css">
            #update_status ul {
                margin: 0px;
                padding-left: 28px;
            }
            #update_status li {
                list-style: none;
                font-size: 13px;
            }
            #update_status li:before {
                content: "•";
                font-size: 20px;
                vertical-align: bottom;
                line-height: 16px;
                margin-right: 3px;
            }
        </style>
CHART;
    }

    function display_licence($type, $title) {
        if ($this->data[$type] > 0) {
            if ($this->data['too_much_' . $type])
                echo '<p class="alert alert-error">';
            else
                echo '<p class="alert alert-success">';
            echo $title . ' <strong>' . $this->data['installed_' . $type] . ' / ' . $this->data[$type];
            echo '</strong></p>';
        }
    }
}

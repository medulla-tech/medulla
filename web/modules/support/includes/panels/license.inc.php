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


$options = array(
    "class" => "LicensePanel",
    "id" => "license",
    "refresh" => 3600,
    "title" => _T("Subscription info", "support"),
);

class LicensePanel extends Panel {

    function __construct($id, $title) {
        parent::__construct($id, $title);
        $this->data = array_merge(array(
            'name' => '',
            'phone' => '',
            'phone_uri' => '',
            'email' => '',
            'email_uri' => '',
            'hours' => '',
            'links' => '',
            'raw_content' => '',
        ), $this->data);
    }

    function display_content() {

        if ($this->data['name'] != ''||$this->data['phone'] != ''||$this->data['email'] != ''||$this->data['hours'] != ''){ 
            echo '<div class="subpanel">';
            echo '<p><b>' . _T('Support', 'support') . '</b></p>';

            if ($this->data['phone'] != '') {
                echo '<p>' . _T("Phone", "support") . ':</p>';
                echo '<p><b><a href="'. $this->data["phone_uri"] . '">' . $this->data['phone'] . '</a></b></p>';
            }
            if ($this->data['email'] != '') {
                echo '<p>' . _T("Email", "support") . ':</p>';
                echo '<p><b><a href="'. $this->data["email_uri"] . '">' . $this->data['email'] . '</a></b></p>';
            }
            if ($this->data['hours'] != ''){
                echo '<p>' . _T("Hours", "support") . ':</p>';
                echo '<p><b>' . $this->data['hours'] . '</b></p>';
            }
            echo '</div>';
        }

        $subscription_info = xmlCall("support.get_subscription_info");
        $display_renew_links = False;
        if ($subscription_info) {
            echo '<div class="subpanel">';
            echo '<p>' . _T("Your subscription", "support") . ':</p>';


            /* Machines */
            list($used_machines, $max_machines, $ts_expiration) = $subscription_info;

            $machine_alert = 'alert-success';

            if ($max_machines == 5) { // If demo, alert is always success
                $display_renew_links = True;
            }
            elseif ($max_machines - $used_machines <= 10) {
                $machine_alert = ''; // warning alert
                $display_renew_links = True;
            }

            echo '<p class="alert ' . $machine_alert  . '">' . _T('Computers', 'support') . ': <b>' . $used_machines. " " . '/' .' '. $max_machines .' ' . '</b></p>';

            /* end support */
            $support_alert = 'alert-success';

            if (time() > $ts_expiration - (86400*30)) { // support is about to expire
                $support_alert = ''; // warning alert
                $display_renew_links = True;
            }
            elseif (time() >= $ts_expiration) { // support is expired
                $support_alert = 'alert-error';
                $display_renew_links = True;
            }

            if ($ts_expiration != 0) { // do not display end of support in case of demo
                echo '<p class="alert ' . $support_alert  . '">' . _T('End', 'support') . ': <b>' . date('Y-m-d', $ts_expiration) .' ' . '</b></p>';
            }
            echo '</div>';
        }

        if ($this->data['raw_content'] != '') {
            echo '<div class="subpanel">';
            echo $this->data['raw_content'];
            echo '</div>';
        }
        if ($this->data['links'] != '') {
            echo '<div class="subpanel">';
            echo '<p>' . _T("Links", "support") . ':</p>';
            foreach($this->data['links'] as $key => $linkgrp){
                if ($linkgrp['url'] != '' && $linkgrp['text'] != '') {
                    if (in_array($key, array('buy_link', 'renew_link'))) {
                        if ($display_renew_links) {
                            echo '<p><b><a href="' . $linkgrp["url"] . '" target="_blank">' . $linkgrp["text"] . '</a></b></p>';
                        }
                    }
                    else {
                        echo '<p><b><a href="' . $linkgrp["url"] . '" target="_blank">' . $linkgrp["text"] . '</a></b></p>';
                    }
                }
            }
            if ($display_renew_links) {
                echo '<p><b><a href="http://' . $_SERVER['HTTP_HOST'] . '/pulse-first-run/?reactivate=1" target="_blank">' . _T('Activate', 'support') . '</a></b></p>';
            }
            echo '</div>';
        }
    }
}
?>

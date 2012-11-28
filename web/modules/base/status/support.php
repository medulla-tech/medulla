<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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

require_once("modules/base/includes/users-xmlrpc.inc.php");

require("graph/navbar.inc.php");
require("includes/statusSidebar.inc.php");
$p = new PageGenerator(_("License and support informations"));
$p->displayTitle();

$subscription = getSubscriptionInformation(True);

$subscription['product_name'] = implode($subscription['product_name'], _(" and "));
if ($subscription['is_subsscribed']) {
    $warn = array();
    if ($subscription['too_much_users']) {
        $warn[] = _('WARNING: The number of registered users is exceeding your license.');
    }
    if ($subscription['too_much_computers']) {
        $warn[] = _('WARNING: The number of registered computers is exceeding your license.');
    }
    if (count($warn) > 0) {
        $warn[] = _('Please contact your administrator for more information. If you are an administrator, please go to the license status page for more information.');
        print sprintf("<div id=\"alert\">%s</div><br/>", implode($warn, '<br/>'));
    }
}

$labels = array(
    'product_name'=>_('Product name'),
    'vendor_name'=>_('Product vendor'),
    'vendor_mail'=>_('Product vendor mail'),
    'customer_name'=>_('Company name'),
    'customer_mail'=>_('Company administrator mail'),
    'comment'=>_('Comment'),
    'users'=>_('Registered users'),
    'computers'=>_('Registered computers'),
    'support_mail'=>_('Support mail address'),
    'support_phone'=>_('Support phone number'),
    'support_comment'=>_('Comment'),
);

$is_mail = array(
    'vendor_mail'=>true,
    'customer_mail'=>true,
    'support_mail'=>true
);

$lines = array();
foreach (array('product_name', 'vendor_name', 'vendor_mail', 'customer_name', 'customer_mail') as $l) {
    if (isset($is_mail[$l])) {
        $lines[]= array($labels[$l], sprintf("<a href='mailto:%s'>%s</a>", $subscription[$l], $subscription[$l]));
    } else {
        $lines[]= array($labels[$l], $subscription[$l]);
    }
}

if (isset($subscription['comment'])) {
    $lines[]= array($labels['comment'], $subscription['comment']);
}

$lines[]= array('', '');

foreach (array( 'support_mail', 'support_phone', 'support_comment') as $l) {
    if (isset($is_mail[$l])) {
        $lines[]= array($labels[$l], sprintf("<a href='mailto:%s'>%s</a>", $subscription[$l], $subscription[$l]));
    } else {
        $lines[]= array($labels[$l], $subscription[$l]);
    }
}

$lines[]= array('', '');

$error = ' style="color:red; font-style:bold;"';
$user_style = '';
if ($subscription['too_much_users']) { $user_style = $error; }
$lines[]= array($labels['users'], sprintf("<p%s>%s / %s</p>", $user_style, $subscription['installed_users'], $subscription['users']));

$user_style = '';
if ($subscription['too_much_computers']) { $user_style = $error; }
$lines[]= array($labels['computers'], sprintf("<p%s>%s / %s</p>", $user_style, $subscription['installed_computers'], $subscription['computers']));


$table = new Table();
$table->setLines($lines);
$table->displayTable(true);


?>

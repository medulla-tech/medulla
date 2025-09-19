<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 * file: ajaxManageProviders.php
 */
require_once("modules/xmppmaster/includes/html.inc.php");
require_once("modules/admin/includes/xmlrpc.php");
?>
<style>
#container>form>table>thead td:first-child span {
    display: block;
    text-align: left;
    padding-left: 0 !important;
    margin-left: 0 !important;
}
#container>form>table>thead td:last-child span {
        display: block;
        text-align: right;
        padding-right: 12px;
}
</style>
<?php
require_once("modules/xmppmaster/includes/html.inc.php");
require_once("modules/admin/includes/xmlrpc.php");

$login       = $_SESSION['login'] ?? '';
$client = $_SESSION['o']     ?? 'MMC';

// root -> all (sees everything), otherwise filtered
$providers = xmlrpc_get_providers($login, strcasecmp($login,'root')===0 ? 'ALL' : $client);
if (empty($providers)) {
    echo '<div style="width:50%;margin:0 auto;background:#e0e0e0;padding:10px;text-align:center;font-size:14px;border-radius:5px;border:1px solid #b0b0b0;">'
       . htmlspecialchars(_T("No providers for this scope.", "admin"), ENT_QUOTES, 'UTF-8')
       . '</div>';
    $f = new ValidatingForm(["action" => urlStrRedirect("admin/admin/index", [])]);
    $f->addValidateButtonWithValue("cancel", "return");
    $f->pop(); $f->display();
    return;
}

$names       = [];
$clients     = [];
$clientIDs   = [];
$uids        = [];
$givenNames  = [];
$sns         = [];
$mails       = [];

// Actions
$editActions   = [];
$deleteActions = [];
$params        = [];

foreach ($providers as $p) {
    $provId      = (int)($p['id'] ?? 0);
    $provName    = (string)($p['name'] ?? '');
    $provClient  = (string)($p['client_name'] ?? '');
    $clientId    = (string)($p['client_id'] ?? '');
    $ldapUid     = (string)($p['ldap_uid'] ?? '');
    $ldapGN      = (string)($p['ldap_givenName'] ?? '');
    $ldapSN      = (string)($p['ldap_sn'] ?? '');
    $ldapMail    = (string)($p['ldap_mail'] ?? '');

    $names[]      = htmlspecialchars($provName,   ENT_QUOTES, 'UTF-8');
    $clients[]    = htmlspecialchars($provClient, ENT_QUOTES, 'UTF-8');
    $clientIDs[]  = htmlspecialchars($clientId,   ENT_QUOTES, 'UTF-8');
    $uids[]       = htmlspecialchars($ldapUid,    ENT_QUOTES, 'UTF-8');
    $givenNames[] = htmlspecialchars($ldapGN,     ENT_QUOTES, 'UTF-8');
    $sns[]        = htmlspecialchars($ldapSN,     ENT_QUOTES, 'UTF-8');
    $mails[]      = htmlspecialchars($ldapMail,   ENT_QUOTES, 'UTF-8');

    $editActions[] = new ActionItem(_T("Edit", "admin"), "editProvider", "edit", "", "admin", "admin");
    $deleteActions[] = new ActionConfirmItem(
        _T("Delete provider", "admin"),
        "deleteProvider",
        "delete",
        "",
        "admin",
        "admin",
        sprintf(
            _T("Delete provider <strong>%s</strong> for client <strong>%s</strong> ?", "admin"),
            htmlspecialchars($provName,   ENT_QUOTES, 'UTF-8'),
            htmlspecialchars($provClient, ENT_QUOTES, 'UTF-8')
        )
    );

    $params[] = [
        'id'             => $provId,
        'client_name'    => $provClient,
        'name'           => $provName,
        'mode'           => 'edit',
    ];
}

$list = new OptimizedListInfos($clients, _T("Client", "admin"));
$list->setNavBar(new AjaxNavBar("10", ''));
$list->disableFirstColumnActionLink();

$list->addExtraInfo($names,    _T("Provider", "admin"));
$list->addExtraInfo($clientIDs, _T("Clients ID", "admin"));
$list->addExtraInfo($uids,       _T("LDAP uid", "admin"));
$list->addExtraInfo($givenNames, _T("LDAP givenName", "admin"));
$list->addExtraInfo($sns,        _T("LDAP sn", "admin"));
$list->addExtraInfo($mails,      _T("LDAP mail", "admin"));

$list->addActionItemArray($editActions);
$list->addActionItemArray($deleteActions);
$list->setParamInfo($params);
$list->display();
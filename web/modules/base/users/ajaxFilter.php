<?php
/**
 * Medulla Management Console (MMC)
 *
 * @copyright Medulla - 2024-2027  <https://medulla-tech.io/>
 * @license   GNU General Public License v2 or later (GPL-2.0+)
 * @link      https://www.gnu.org/licenses/gpl-2.0.html
 *
 * This file is part of Medulla Management Console (MMC).
 *
 * MMC is free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License,
 * or (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 * See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC. If not, see <https://www.gnu.org/licenses/.>
 */
?>
<style>
    #mail {
        color: #016080;
    }

    #mail:hover {
        text-decoration: underline;
    }

    @keyframes rainbow {
        0%, 100% { color: red; }
        16% { color: orange; }
        33% { color: yellow; }
        50% { color: green; }
        66% { color: blue; }
        83% { color: indigo; }
        100% { color: violet; }
    }

    .rainbow-animation {
        animation: rainbow 2s infinite;
        display: inline-block;
    }
</style>

<?php
global $conf;
if(isset($_REQUEST['maxperpage'])) {
    $maxperpage = $_REQUEST['maxperpage'];
} else {
    $maxperpage = $conf["global"]["maxperpage"];
}

$filter = $_GET["filter"];
if (isset($_GET["start"])) {
    $start = $_GET["start"];
} else {
    $start = 0;
}

list($usercount, $users) = get_users_detailed($error, $filter, $start, $start + $maxperpage);

$arrUser = array();
$arrSnUser = array();
$homeDirArr = array();
$mails = array();
$phones = array();
$css = array();

for ($idx = 0; $idx < safeCount($users); $idx++) {
    if ($users[$idx]["enabled"]) {
        $css[$idx] = "userName";
    } else {
        $css[$idx] = "userNameDisabled";
    }
    $arrUser[] = is_object($users[$idx]['uid']) ? $users[$idx]['uid']->scalar : $users[$idx]['uid'];

    $givenName = is_object($users[$idx]['givenName']) ? $users[$idx]['givenName']->scalar : $users[$idx]['givenName'];
    $sn = is_object($users[$idx]['sn']) ? $users[$idx]['sn']->scalar : $users[$idx]['sn'];
    $arrSnUser[] = $givenName.' '.$sn;

    if (!empty($users[$idx]["mail"])) {
        $emailContent = is_object($users[$idx]["mail"]) ? $users[$idx]["mail"]->scalar : $users[$idx]["mail"];
        if (!empty($emailContent)) {
            $mails[] = '<a id="mail" href="mailto:' . htmlspecialchars($emailContent) . '">' . htmlspecialchars($emailContent) . '</a>';
        } else {
            $mails[] = "";
        }
    } else {
        $mails[] = "";
    }
    /* We display the smallest telephone number, hopefully it is the user phone extension */
    $num = null;
    $numArray = [];
    if (!empty($users[$idx]["telephoneNumber"])) {
        foreach ($users[$idx]["telephoneNumber"] as $_number) {
            $number = is_object($_number) ? $_number->scalar : $_number;
            $numArray[] = $number;
        }
        $num = implode("<br>", $numArray); // Concaténer les numéros avec un retour à la ligne
    }
    $phones[] = $num === null ? "" : $num;
}

// Avoiding the CSS selector (tr id) to start with a number
$ids_users = [];
foreach($users as $index => $user) {
    $ids_users[] = 'u_' . $user['uid']->scalar;
}

// $arrUser is the list of all Users
$n = new UserInfos($arrUser, _("Login"));
$n->setcssIds($ids_users);
$n->setItemCount($usercount);
$n->setNavBar(new AjaxPaginator($usercount, $filter, "updateSearchParam", $maxperpage));

$n->start = 0;
$n->end = $usercount - 1;

$n->setCssClass("userName");

$n->css = $css;

$n->addExtraInfo($arrSnUser, _("Name"));
$n->addExtraInfo($mails, _("Mail"));
$n->addExtraInfo($phones, _("Telephone"));

$n->addActionItem(new ActionItem(_("Edit"), "edit", "edit", "user"));
if (in_array("extticket", $_SESSION["supportModList"])) {
    $n->addActionItem(new ActionItem(_("extTicket issue"), "extticketcreate", "extticket", "user"));
}
$n->addActionItem(new ActionItem(_("MMC rights"), "editacl", "editacl", "user"));
$n->addActionItem(new ActionPopupItem(_("Delete"), "delete", "delete", "user"));
if (has_audit_working()) {
    $n->addActionItem(new ActionItem(_("Logged Actions"), "loguser", "audit", "user"));
}
$n->setName(_("Users"));
$n->display();

?>
<script>
// First ever Medulla easteregg
function applyAnimation() {
    var currentDate = new Date();
    currentDate.setHours(0, 0, 0, 0); // normalize the time at midnight to compare only the dates
    var prideDay = new Date(currentDate.getFullYear(), 5, 28);
    prideDay.setHours(0, 0, 0, 0);

    if (currentDate.getTime() === prideDay.getTime()) {
        document.getElementById('mail').classList.add('rainbow-animation');
    }
}
applyAnimation();
</script>
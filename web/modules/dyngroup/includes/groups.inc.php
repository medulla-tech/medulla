<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
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
 *
 */

if (in_array("imaging", $_SESSION["modulesList"])) {
    require_once('modules/imaging/includes/xmlrpc.inc.php');
}
require_once('modules/dyngroup/includes/dyngroup.php'); // for getPGobject method
?>

<style>
    #grouplist {
        color: #444;
        background: #F7FAFD;
        border: 1px solid #b4c7d4;
        border-radius: 10px;
        padding: 26px 28px 20px 28px;
        margin: 22px 0 32px 0;
        width: 750px;
        max-width: 980px;
    }

    .grouplist-flex {
        display: flex;
        flex-direction: row;
        align-items: flex-start;
        gap: 22px;
    }

    .grouplist-col {
        display: flex;
        flex-direction: column;
        min-width: 260px;
        max-width: 320px;
        flex: 1;
    }

    .grouplist-col .list-title {
        font-size: 1.08em;
        color: #2061a6;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .grouplist-col.right .list-title {
        margin-top: 38px;
    }

    .grouplist-col .filter-row {
        display: flex;
        align-items: center;
        margin-bottom: 7px;
        gap: 8px;
    }

    .grouplist-col .filter-row input {
        width: 90%;
        padding: 5px;
        border: 1px solid #b7d0e6;
        border-radius: 4px;
        box-sizing: border-box;
    }

    .grouplist-col .filter-row input[type="text"],
    .grouplist-col .filter-row button {
        box-sizing: border-box;
        height: 28px;
        margin-bottom: 8px;
        margin-right: 8px;
    }

    .grouplist-col .filter-row button img {
        display: block;
        width: 18px;
        height: 18px;
        margin: auto;
    }

    .grouplist-col select.list {
        width: 100%;
        min-width: 210px;
        height: 300px;
        font-size: 1.07em;
        line-height: 1.35;
        font-weight: 500;
        padding: 5px 0;
        border-radius: 4px;
        border: 1px solid #b7d0e6;
        background: #fff;
    }

    select.list option {
        font-size: 1em;
        padding: 4px 10px;
        font-weight: 500;
    }

    .grouplist-buttons-wrapper {
        display: flex;
        align-items: center;
        height: 340px;
    }

    .grouplist-buttons {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-width: 60px;
        gap: 18px;
        width: 54px;
    }

    .grouplist-with-filter .grouplist-buttons {
        margin-top: 53px;
    }

    .grouplist-buttons input[type="image"] {
        background: #fff;
        border: 1px solid #b7d0e6;
        border-radius: 5px;
        width: 32px;
        height: 32px;
        padding: 3px;
    }

    .grouplist-buttons input[type="image"]:hover {
        border-color: #4096d7;
        background: #f3faff;
    }

    /* MASQUE LA SCROLBAR */
    /* Chrome, Edge, Safari */
    select.list::-webkit-scrollbar {
        width: 0px;
        background: transparent;
    }

    /* Firefox */
    select.list {
        scrollbar-width: none;
    }

    h2 {
        margin-top: 8px;
    }

    .label-radio-row {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 8px;
    }

    .label-radio-row label {
        margin: 0;
        font-weight: normal;
        font-size: 1em;
    }

    .label-radio-row input[type="radio"] {
        margin: 0 3px 0 0;
        vertical-align: middle;
    }

    @media (max-width: 900px) {
        #grouplist {
            min-width: unset;
            width: 99%;
        }

        .grouplist-flex {
            flex-direction: column;
        }

        .grouplist-col {
            min-width: unset;
            max-width: 100%;
        }
    }
</style>

<?php

function drawGroupList($machines, $members, $listOfMembers, $visibility, $diff, $gid, $name, $filter = '', $type = 0)
{
    if ($type == 0) {
        $label_name = _T('Group name', 'dyngroup');
        $label_visible = _T('Make favourite', 'dyngroup');
        $label_members = _T("Group members", "dyngroup");
    } else {
        $label_name = _T('Group name', 'dyngroup');
        $label_visible = _T('Make favourite', 'dyngroup');
        $label_members = _T("Group members", "dyngroup");
    }
    $willBeUnregistered = array();
    if ($type == 1) {
        $listOfMembersUuids = array_keys($listOfMembers);
        foreach ($listOfMembersUuids as $target_uuid) {
            $ret = xmlrpc_canIRegisterThisComputer($target_uuid);
            if (!$ret[0]) {
                $willBeUnregistered[] = $target_uuid;
            } elseif ($ret[0] && isset($ret[1]) && $ret[1] != false) {
                $willBeUnregistered[] = $target_uuid;
            }
        }
    }
    $currentGroup = getPGobject($gid, true);
    if ($type == 1) {
        $machinesInProfile = arePartOfAProfile(array_keys($listOfMembers));
        $computersgroupedit = 0;
        if (isset($_GET['action']) && $_GET['action'] == 'computersgroupedit') {
            $computersgroupedit = 1;
            foreach ($machinesInProfile as $uuid => $group) {
                if ($group['groupname'] == $currentGroup->name) {
                    unset($machinesInProfile[$uuid]);
                    unset($willBeUnregistered[array_search($uuid, $willBeUnregistered)]);
                }
            }
        }
    }
?>
    <style>
        #grouplist {
            width: 100%;
            box-sizing: border-box;
        }
        .grouplist-flex {
            display: flex;
            align-items: stretch;
            gap: 12px;
            width: 100%;
        }
        .grouplist-col {
            flex: 1;
            min-width: 0;
            display: flex;
            flex-direction: column;
        }
        .grouplist-col select,
        .grouplist-col select.list {
            width: 100% !important;
            height: auto !important;
            flex: 1;
            box-sizing: border-box;
        }
        .grouplist-col .filter-row input {
            width: auto !important;
            height: auto !important;
        }
        .grouplist-buttons-wrapper {
            display: flex;
            align-items: center;
            flex-direction: column;
            justify-content: center;
            gap: 8px;
            flex-shrink: 0;
        }
        .grouplist-buttons {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
    </style>
    <form action="<?php echo $_SERVER["REQUEST_URI"]; ?>" method="post">
        <table class="mmc-form-table" style="margin-bottom:18px;">
            <tr class="mmc-form-row">
                <td class="mmc-label"><?php echo $label_name; ?></td>
                <td><input name="name" value="<?php echo $name ?>" type="text" /></td>
            </tr>
            <tr class="mmc-form-row">
                <td class="mmc-label"><?php echo $label_visible; ?></td>
                <td class="radio-inline">
                    <label><input name="visible" value="show" type="radio" <?php if ($visibility == 'show') echo 'checked'; ?>><?php echo _T('Yes', 'dyngroup') ?></label>
                    <label><input name="visible" value="hide" type="radio" <?php if ($visibility != 'show') echo 'checked'; ?>><?php echo _T('No', 'dyngroup') ?></label>
                </td>
            </tr>
        </table>
        <div id="grouplist">
            <div class="grouplist-flex grouplist-with-filter">
                <div class="grouplist-col">
                    <div class="list-title"><?php echo  _T("All machines", "dyngroup"); ?></div>
                    <div class="filter-row" style="display:flex; margin-bottom:8px;">
                        <input name='filter' type='text' value='<?php echo  $filter ?>' placeholder="Filtrer..." style="flex:1; min-width:0; width:auto !important; height:auto !important; padding:6px 10px; border:1px solid #ccc; border-radius:4px 0 0 4px; border-right:none; font-size:13px;" />
                        <button type="submit" name="bfiltmachine" style="padding:6px 10px; border:1px solid #ccc; border-radius:0 4px 4px 0; background:#f5f5f5; cursor:pointer; display:flex; align-items:center;" tabindex="-1">
                            <img src="img/actions/display.svg" width="18" height="18" alt="Filtrer" style="filter:brightness(0);" />
                        </button>
                    </div>
                    <select multiple size="15" class="list" name="machines[]">
                        <?php
                        foreach ($diff as $idx => $machine) {
                            if ($machine == "") {
                                unset($machines[$idx]);
                                continue;
                            }
                            echo "<option value=\"" . $idx . "\">" . $machine . "</option>\n";
                        }
                        ?>
                    </select>
                </div>
                <div class="grouplist-buttons-wrapper">
                    <div class="grouplist-buttons">
                        <input type="image" name="baddmachine" src="img/other/right.svg" width="25" height="25" alt="Ajouter" title="Ajouter" />
                        <input type="image" name="bdelmachine" src="img/other/left.svg" width="25" height="25" alt="Retirer" title="Retirer" />
                    </div>
                </div>
                <div class="grouplist-col">
                    <div style="height: 44px"></div>
                    <div class="list-title"><?php echo  $label_members; ?></div>
                    <select multiple size="15" class="list" name="members[]">
                        <?php
                        foreach ($members as $idx => $member) {
                            $currentUuid = explode('##', $idx);
                            $currentUuid = $currentUuid[1];
                            if ($member == "") {
                                unset($members[$idx]);
                                continue;
                            }
                            $style = '';
                            if ($type == 1) {
                                if (in_array($currentUuid, array_keys($machinesInProfile))) {
                                    $style = 'background: red; color: white;';
                                } elseif (in_array($currentUuid, $willBeUnregistered)) {
                                    $style = 'background: purple; color: white;';
                                }
                            }
                            echo "<option style=\"" . $style . "\" value=\"" . $idx . "\">" . $member . "</option>\n";
                        }
                        ?>
                    </select>
                </div>
            </div>
        </div>
        <?php
        if ($type == 1) {
            $warningMessage = false;
            if (safeCount($machinesInProfile) > 0) {
                $warningMessage = true;
                print '<p style="margin:14px 0 4px 0;color:#d9534f;font-weight:bold;">';
                print _T('Computers listed below are already part of another imaging group.', 'dyngroup');
                echo '<ul style="margin-left:20px;">';
                foreach ($machinesInProfile as $machineUuid => $group) {
                    printf(
                        _T('<li>%s is part of <a href="%s">%s</a></li>'),
                        $listOfMembers[$machineUuid]['hostname'],
                        urlStrRedirect('imaging/manage/display', array('gid' => $group['groupid'], 'groupname' => $group['groupname'])),
                        $group['groupname']
                    );
                }
                echo '</ul></p>';
            }
            $standAloneImagingRegistered = array_diff($willBeUnregistered, array_keys($machinesInProfile));
            if (safeCount($standAloneImagingRegistered) > 0) {
                $warningMessage = true;
                print '<p style="margin:12px 0 4px 0;color:#b44;font-weight:bold;">';
                print _T('Computers listed below are already stand-alone registered in imaging.', 'dyngroup');
                echo '<ul style="margin-left:20px;">';
                foreach ($standAloneImagingRegistered as $machineUuid) {
                    printf('<li>%s</li>', $listOfMembers[$machineUuid]['hostname']);
                }
                echo '</ul></p>';
            }

            if ($warningMessage) {
                echo '<div style="color:#be441e;font-weight:600;margin:8px 0 8px 0;">';
                echo _T('<p>These computers will be moved to this group and their bootmenus <strong>will be rewritten</strong></p>', 'dyngroup');
                echo '<p>' . _T('All related images to these computers will be <strong>DELETED</strong>', 'dyngroup') . '</p>';
                echo '</div>';
            }
        }
        ?>
        <input type="hidden" name="type" value="<?php echo  $type; ?>" />
        <input type="hidden" name="lmachines" value="<?php echo base64_encode(serialize($machines)); ?>" />
        <input type="hidden" name="lmembers" value="<?php echo base64_encode(serialize($members)); ?>" />
        <input type="hidden" name="lsmembers" value="<?php echo base64_encode(serialize($listOfMembers)); ?>" />
        <input type="hidden" name="willBeUnregistered" value="<?php echo base64_encode(serialize($willBeUnregistered)); ?>" />
        <input type="hidden" name="computersgroupedit" value="<?php echo isset($computersgroupedit) ? $computersgroupedit : ""; ?>" />
        <input type="hidden" name="id" value="<?php echo  $gid ?>" />
        <div style="margin-top:14px;">
            <input type="submit" name="bconfirm" class="btnPrimary" value="<?php echo  _("Confirm"); ?>" />
            <input type="submit" name="breset" class="btnSecondary" value="<?php echo  _("Cancel"); ?>" />
        </div>
    </form>
<?php
}

function drawGroupShare($nonmemb, $members, $listOfMembers, $diff, $gid, $name)
{
?>
    <form action="<?php echo $_SERVER["REQUEST_URI"]; ?>" method="post">
        <input name="name" value="<?php echo $name ?>" type="hidden" />
        <div id="grouplist">
            <div class="grouplist-flex">
                <div class="grouplist-col">
                    <div class="list-title"><?php echo _T("All share entities", "dyngroup"); ?></div>
                    <select multiple size="15" class="list" name="nonmemb[]">
                        <?php
                        foreach ($diff as $idx => $user) {
                            if ($user == "") {
                                unset($nonmemb[$idx]);
                                continue;
                            }
                            if ($user == "root") continue;
                            $style = '';
                            $ma = preg_split("/##/", $idx);
                            if ($ma[0] == 1) $style = ' style="background-color: #eedd00;"';
                            echo "<option$style value=\"" . $idx . "\">" . $user . "</option>\n";
                        }
                        ?>
                    </select>
                </div>
                <div class="grouplist-buttons-wrapper">
                    <div class="grouplist-buttons">
                        <input type="image" name="badduser" src="img/other/right.svg" width="25" height="25" alt="Ajouter" title="Ajouter" /><br />
                        <input type="image" name="bdeluser" src="img/other/left.svg" width="25" height="25" alt="Retirer" title="Retirer" />
                    </div>
                </div>
                <div class="grouplist-col">
                    <div class="list-title"><?php echo _T("Group share", "dyngroup"); ?></div>
                    <select multiple size="15" class="list" name="members[]">
                        <?php
                        foreach ($members as $idx => $member) {
                            if ($member == "") {
                                unset($members[$idx]);
                                continue;
                            }
                            if ($member == "root") continue;
                            $style = '';
                            $ma = preg_split("/##/", $idx);
                            if ($ma[0] == 1) $style = ' style="background-color: #eedd00;"';
                            echo "<option$style value=\"" . $idx . "\">" . $member . "</option>\n";
                        }
                        ?>
                    </select>
                </div>
            </div>
        </div>
        <input type="hidden" name="lnonmemb" value="<?php echo base64_encode(serialize($nonmemb)); ?>" />
        <input type="hidden" name="lmembers" value="<?php echo base64_encode(serialize($members)); ?>" />
        <input type="hidden" name="lsmembers" value="<?php echo base64_encode(serialize($listOfMembers)); ?>" />
        <input type="hidden" name="id" value="<?php echo $gid ?>" />
        <div style="margin-top:14px;">
            <input type="submit" name="bconfirm" class="btnPrimary" value="<?php echo _("Confirm"); ?>" />
            <input type="submit" name="breset" class="btnSecondary" value="<?php echo _("Cancel"); ?>" />
        </div>
    </form>
<?php
}

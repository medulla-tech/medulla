<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

function check_auth($login, $pass) {    
    $param = array();
    $param[] = $login;
    $param[] = prepare_string($pass);
    return xmlCall("base.ldapAuth", $param);
}

function auth_user ($login, $pass, $error)
{
    global $conf;
    global $error;
    
    if (($login == "") || ($pass == "")) return false;

    $param = array();
    $param[] = $login;
    $param[] = prepare_string($pass);

    //put server selected in $_SESSION
    $urlArr = parse_url($_POST["server"]);
    $_SESSION["XMLRPC_agent"] = $urlArr;
    
    $ret = xmlCall("base.ldapAuth",$param);    
    if ($ret != "1") {
        if (!isXMLRPCError()) {
            $error = _T("Invalid login");
        }
        return false;
    }
    
    return true;
}

/**
 * get an array of ldap users via cpu
 * @return list of users in an array of ldap users
 * @param &$error referenced error String
 */
function get_users(&$error)
{
    $tab = xmlCall("base.getUsersLdap",null);
    $resTab = array();
    foreach ($tab as $tmpTab)
    {
        $resTab[]=$tmpTab["uid"];
    }

    return $resTab;
}

/**
 * @return get a detailled ldap users using cpu
 * @param &$error reference String error
 */
function get_users_detailed(&$error, $filter = null, $start = null, $end = null)
{
    if ($filter == "") $filter = null;
    else $filter = "*".$filter . "*";
    return xmlCall("base.searchUserAdvanced", array($filter, $start, $end));
}

/**
 * add a user
 * @param $login user's login
 * @param $pass user's pass
 * @param $firstname user's firstname
 * @param $name user's name
 * @param $homedir user home directory
 */
function add_user($login, $pass, $firstname, $name, $homedir, $primaryGroup = "")
{
    $param = array($login, prepare_string($pass), $firstname, $name, $homedir, $primaryGroup);
    $ret = xmlCall("base.createUser", $param);    
    return sprintf(_("user %s created<br />"), $login);
}

function del_user($login, $files)
{
   callPluginFunction("delUser",$login);
   if ($files=="on") {$fichier=1;} else {$fichier=0;}
   $param=array ($login,$fichier);
   xmlCall("base.delUserFromAllGroups", $login);
   return xmlCall("base.delUser",$param);
}

function getAllGroupsFromUser($uid) {
    return xmlCall("base.getAllGroupsFromUser",array($uid));
}

function getUserDefaultPrimaryGroup() {
    return xmlCall("base.getUserDefaultPrimaryGroup",null);
}

function getUserPrimaryGroup($uid) {
    return xmlCall("base.getUserPrimaryGroup",array($uid));
}

function getUserSecondaryGroups($uid) {
    return xmlCall("base.getUserSecondaryGroups",array($uid));
}

function exist_user($uid) {
  return xmlCall("base.existUser",$uid);
}

function maxUID() {
  return xmlCall("base.maxUID",null);
}

function maxGID() {
  return xmlCall("base.maxGID",null);
}

function getAcl($uid) {
  return xmlCall("base.getUserAcl",array($uid));
}

function setAcl($uid,$aclString) {
  return xmlCall("base.setUserAcl",array($uid,$aclString));
}


function move_home($uid,$newHome) {
  return xmlCall("base.moveHome",array($uid,$newHome));
}

function getDetailedUser($uid) {
  return xmlCall("base.getDetailedUser",$uid);
}


function change_user_main_attr($uid, $newuid, $firstname, $surname) {
  return xmlCall("base.changeUserMainAttributes",array($uid, $newuid, $firstname, $surname));
}

function isEnabled($uid) {
    return xmlCall("base.isEnabled", $uid);
}

function enableUser($uid) {
    return xmlCall("base.enableUser", $uid);
}

function disableUser($uid) {
    return xmlCall("base.disableUser", $uid);
}

function changeUserAttributes($uid,$attr,$attrval) {
    return xmlCall("base.changeUserAttributes", array($uid,$attr,$attrval));
}

function changeUserTelephoneNumbers($uid, $numbers) {
    $update = array();
    foreach($numbers as $number) if (strlen($number)) $update[] = $number;
    if (empty($update)) $update = null;
    xmlCall("base.changeUserAttributes", array($uid, "telephoneNumber", $update));
}

?>

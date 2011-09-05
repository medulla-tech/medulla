<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2010 Mandriva, http://www.mandriva.com/
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

/* Definition of all the ppolicy module XML-RPC calls */

function checkPPolicy($ppolicy) {
    return xmlCall("ppolicy.checkPPolicy",array($ppolicy));
}

function addPPolicy($ppolicy, $desc = "") {
    return xmlCall("ppolicy.addPPolicy",array($ppolicy, $desc));
}

function getDefaultPPolicy() {
    return xmlCall("ppolicy.getDefaultPPolicy", array());
}

function removePPolicy($ppolicy) {
    return xmlCall("ppolicy.removePPolicy",array($ppolicy));
}

function listPPolicy($filter = "") {
    return xmlCall("ppolicy.listPPolicy", array($filter));
}

function getPPolicyAttribute($name, $ppolicy) {
    return xmlCall("ppolicy.getPPolicyAttribute",array($name, $ppolicy));
}

function getAllPPolicyAttributes($ppolicy) {
    return xmlCall("ppolicy.getAllPPolicyAttributes",array($ppolicy));
}

function setPPolicyAttribute($name, $value, $ppolicy) {
    return xmlCall("ppolicy.setPPolicyAttribute",array($name, $value, $ppolicy));
}

function getDefaultPPolicyAttributes() {
    return xmlCall("ppolicy.getDefaultPPolicyAttributes",array());
}

function setPPolicyDefaultConfigAttributes() {
    return xmlCall("ppolicy.setPPolicyDefaultConfigAttributes",array());
}

/* ppolicy user */

function hasUserPPolicy ($uid) {
    return xmlCall("ppolicy.hasUserPPolicy",array($uid));
}

function getUserPPolicy ($uid) {
    return xmlCall("ppolicy.getUserPPolicy",array($uid));
}

function addUserPPolicy ($uid, $ppolicy = null) {
    return xmlCall("ppolicy.addUserPPolicy",array($uid, $ppolicy));
}

function updateUserPPolicy ($uid, $ppolicy = null) {
    return xmlCall("ppolicy.updateUserPPolicy",array($uid, $ppolicy));
}

function removeUserPPolicy ($uid) {
    return xmlCall("ppolicy.removeUserPPolicy",array($uid));
}

function getUserPPolicyAttribut($uid,$name) {
    return xmlCall("ppolicy.getUserPPolicyAttribut",array($uid,$name));
}

function setUserPPolicyAttribut($uid,$name,$value) {
    return xmlCall("ppolicy.setUserPPolicyAttribut",array($uid,$name,$value));
}

function isAccountLocked($uid) {
    return xmlCall("ppolicy.isAccountLocked", array($uid));
}

function lockAccount($uid) {
    return xmlCall("ppolicy.lockAccount", array($uid));
}

function unlockAccount($uid) {
    return xmlCall("ppolicy.unlockAccount", array($uid));
}

function passwordMustBeChanged($uid) {
    return xmlCall("ppolicy.passwordMustBeChanged", array($uid));
}

function passwordHasBeenReset($uid) {
    return xmlCall("ppolicy.passwordHasBeenReset", array($uid));
}

function userMustChangePassword($uid) {
    return xmlCall("ppolicy.userMustChangePassword", array($uid));
}

function isAccountInGraceLogin($uid) {
    return xmlCall("ppolicy.isAccountInGraceLogin", array($uid));
}

function isPasswordExpired($uid) {
    return xmlCall("ppolicy.isPasswordExpired", array($uid));
}

?>

<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2010 Mandriva, http://www.mandriva.com
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

/**
 * Declare all Modifiable PPolicy Attribute :
 *  variable name associated tuple :
 *      - usual name
 *      - variable type
 *
 * It's use to work on right variable among $_POST array.
 * It doesn't set form's input field !
 *
 */

function getPPolicyAttributesKeys() {
    return array(   "pwdMinLength"          => array(_T("Minimum length", "ppolicy"), "int"),
                    "pwdMinAge"             => array(_T("Minimum age", "ppolicy"), "int"),
                    "pwdMaxAge"             => array(_T("Maximum age", "ppolicy"), "int"),
                    "pwdMustChange"         => array(_T("Change password on first connection", "ppolicy"), "bool"),
                    "pwdLockoutDuration"    => array(_T("Lockout duration", "ppolicy"), "int"),
                    "pwdMaxFailure"         => array(_T("Maximum failed", "ppolicy"), "int"),
                    "pwdLockout"            => array(_T("Preventive lockout user", "ppolicy"), "bool"),
                    "pwdInHistory"          => array(_T("Password hash history", "ppolicy"), "int"),
                    "pwdGraceAuthNLimit"    => array(_T("Number of grace authentications", "ppolicy"), "int"),
                    "pwdReset"              => array(_T("Reset the password", "ppolicy"), "bool"),
                    "pwdCheckQuality"       => array(_T("Password policy quality check"), "int"),
                    "description"           => array(_T("Description"), "string"),
                    );
}

function ppolicyTips($attr) {
    $tips = array(
                  "pwdMinLength" => _T("this attribute contains the minimum number of characters that will be accepted in a password", "ppolicy"),
                  "pwdMinAge" => _T("This attribute holds the number of seconds that must elapse between modifications to the password. If this attribute is not present, 0 seconds is assumed (i.e. the password may be modified whenever and however often is desired).", "ppolicy"),
                  "pwdMaxAge" => _T("This attribute holds the number of seconds after which a modified password will expire. If this attribute is not present, or if the value is 0 the password does not expire.", "ppolicy"),
                  "pwdMustChange" => _T("This flag specifies whether users must change their passwords when they first bind to the directory after a password is set or reset by the administrator.", "ppolicy"),
                  "pwdInHistory" => _T("This attribute is used to specify the maximum number of used passwords. If the attribute is not present, or if its value is 0, used passwords will not be stored and thus any previously-used password may be reused.", "ppolicy"),
                  "pwdLockout" => _T("This flag indicates, when enabled, that the password may not be used to authenticate after a specified number of consecutive failed bind attempts. The maximum number of consecutive failed bind attempts is specified in the \"Password maximum failure\" field below.", "ppolicy"),
                  "pwdMaxFailure" => _T("This attribute specifies the number of consecutive failed bind attempts after which the password may not be used to authenticate. If this attribute is not present, or if the value is 0, this policy is not checked, and the value of \"Preventive user lockout\" will be ignored.", "ppolicy"),
                  "pwdLockoutDuration" => _T("This attribute holds the number of seconds that the password cannot be used to authenticate due to too many failed authentication attempts. If this attribute is empty, or if the value is 0 the password cannot be used to authenticate until reset by a password administrator.", "ppolicy"),
                  "pwdGraceAuthNLimit" => _T("This attribute contains the number of times that an expired password may be used to authenticate a user to the directory. If this attribute is not present or if its value is zero, users with expired password will not be allowed to authenticate.", "ppolicy"),
                  "pwdReset" => _T("This flag allows to mark the password as having being reset by an administrator.", "ppolicy"),
                  "pwdCheckQuality" => _T("This attribute indicates how the password quality will be verified while being modified or added. If this attribute is not present, or if the value is '0', quality checking will not be enforced.  A value of '1' indicates that the server will check the quality, and if the server is unable to check it (due to a hashed password or other reasons) it will be accepted. A value of '2' indicates that the server will check the quality, and if the server is unable to verify it, it will return an error refusing the password.", "ppolicy"),
                  );
    return $tips[$attr];
}

$x = "Default password policy";

?>

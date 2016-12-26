<?php
/*
 * (c) 2015-2016 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
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

//Convert string characters to hexadecimal code
function strtohex($string)
{
  $string = str_split($string);
  foreach($string as &$char)
    $char = dechex(ord($char));
  return implode('',$string);
}

//Crypt the string parameter for normal Windows password
/*
	1 - Add 'Password' to string
	2 - Convert each character of the string to hexadecimal
	3 - Insert 00h between each converted character
	4 - Convert the converted hexa string to base64 string
*/
function cryptSysprepPassword($string)
{
	$string .= 'Password';
	$strArray = str_split($string);
	$hex = array();
	foreach($strArray as $char)
	{
		$hex[] = strtohex($char);
		$hex[] = '00';
	}
	$hex = implode($hex);

	return base64_encode(pack('H*',$hex));
}

//Crypt the string parameter for administrator  Windows password
/*
	1 - Add 'AdministratorPassword' to string
	2 - Convert each character of the string to hexadecimal
	3 - Insert 00h between each converted character
	4 - Convert the converted hexa string to base64 string
*/
function cryptSysprepAdminPassword($string)
{
	$string .= 'AdministratorPassword';
	$strArray = str_split($string);
	$hex = array();
	foreach($strArray as $char)
	{
		$hex[] = strtohex($char);
		$hex[] = '00';
	}
	$hex = implode($hex);

	return base64_encode(pack('H*',$hex));
}

// Conditions executed by data_windows_Answer_file_generator.inc.php which post $_GET['data'] and $_GET['passwordType'] by ajax call
if($_GET['passwordType'] == 'admin')
{
	$password = cryptSysprepAdminPassword($_GET['data']);
}
else
{
	$password = cryptSysprepPassword($_GET['data']);
}
echo $password;
?>
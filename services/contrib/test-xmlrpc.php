#!/usr/bin/php
/*
 * (c) 2008 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Pulse 2, http://pulse2.mandriva.org
 *
 * Pulse 2 is free software; you can redistribute it and/or modify
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
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
 * MA 02110-1301, USA
 */

<?php

function decode_entities($text) {
    $text = html_entity_decode($text,ENT_QUOTES,"ISO-8859-1"); /* NOTE: UTF-8 does not work! */
    $text= preg_replace('/&#(\d+);/me',"chr(\\1)",$text); /* decimal notation */
    $text= preg_replace('/&#x([a-f0-9]+);/mei',"chr(0x\\1)",$text);  /* hex notation */
    return $text;
}

if (!isset($conf["global"]["login"])) {
    $conf["login"] = "";
    $conf["password"] = "";
    $conf["host"] = "127.0.0.1";
    $conf["port"] = "8001";
    $conf["scheme"] = "http";
    $conf["debug"]["level"]="0";
}

$params = $_SERVER["argv"];
array_shift($params);
$method = array_shift($params);

$output_options = array( "output_type" => "xml", "verbosity" => "pretty", "escaping" => array("markup", "non-ascii", "non-print"), "version" => "xmlrpc", "encoding" => "UTF-8" );

$method="sync_remote_exec";
$params=array(
    1,
    "cd /tmp; more.com OOo2.log.txt",
    array(
        'host'=> 'pulse2-win2k',
        'protocol'=> 'ssh'
    )
    );

$request = xmlrpc_encode_request($method, $params, $output_options);
/*
if ($params == null) {
    $request = xmlrpc_encode_request($method, null, $output_options);
} else {
    $request = xmlrpc_encode_request($method, $params, $output_options);
    $request = decode_entities($request, ENT_QUOTES, "UTF-8");
}
*/
/* We build the HTTP POST that will be sent */
$host= $conf["host"].":".$conf["port"];
$url = "/";
$httpQuery = "POST ". $url ." HTTP/1.0\r\n";
$httpQuery .= "User-Agent: xmlrpc\r\n";
$httpQuery .= "Host: ". $host ."\r\n";
$httpQuery .= "Content-Type: text/xml\r\n";
$httpQuery .= "Content-Length: ". strlen($request) . "\r\n";

$httpQuery .= "Authorization: Basic ".base64_encode($conf["login"].":".$conf["password"]) . "\r\n\r\n";
$httpQuery .= $request;

$sock = null;

/* Connect to the XML-RPC server */
if ($conf["scheme"] == "https") {
    $prot = "ssl://";
}
$errLevel = error_reporting();
error_reporting(0);
$sock = fsockopen($prot.$conf["host"], $conf["port"], $errNo, $errString);
error_reporting($errLevel);
if (!$sock) {
    print("Can't connect to the agent\n");
    exit(-1);
}

/* Send the HTTP POST */
if ( !fwrite($sock, $httpQuery, strlen($httpQuery)) ) {
    print("Can't send XML-RPC request to MMC agent");
    exit(-1);
}
fflush($sock);

/* Get the response from the server */
while (!feof($sock)) {
    $xmlResponse .= fgets($sock);
}
fclose($sock);

/* Process the response */
if (!strlen($xmlResponse)) {
    print("MMC agent communication problem");
    exit(-1);
}

/* Process the received HTTP header */
$pos = strpos($xmlResponse, "\r\n\r\n");
$httpHeader = substr($xmlResponse, 0, $pos);
if ($method == "base.ldapAuth") {
    /* The RPC server must send us a session cookie */
    if (preg_match("/(TWISTED_SESSION=[0-9a-f]+);/", $httpHeader, $match) > 0) {
        $_SESSION["RPCSESSION"] = $match[1];
    } else {
        /* Can't get a session from the Twisted XML-RPC server */
        print("MMC agent communication problem");
        exit(-1);
    }
}

/* Process the XML response */
$xmlResponse = substr($xmlResponse, $pos + 4);
/*
   Test if the XMLRPC result is a boolean value set to False.
   If it is the case, xmlrpc_decode will return an empty string.
   So we need to test this special case.
*/
$booleanFalse = "<?xml version='1.0'?>\n<methodResponse>\n<params>\n<param>\n<value><boolean>0</boolean></value>\n</param>\n</params>\n</methodResponse>\n";
if ($xmlResponse == $booleanFalse) $xmlResponse = "0";
else {
    $xmlResponseTmp = xmlrpc_decode($xmlResponse, "UTF-8");
    /* if we cannot decode in UTF-8 */
    if (!$xmlResponseTmp) {
        /* Maybe we received data encoded in ISO latin 1, so convert them
           to UTF8 first*/
        $xmlResponse = iconv("ISO-8859-1", "UTF-8", $xmlResponse);
        $xmlResponse = xmlrpc_decode($xmlResponse, "UTF-8");
    } else {
        $xmlResponse = $xmlResponseTmp;
    }
}

/* If debug is on, print the XML-RPC call and result */
if ($conf["debug"]["level"]!=0) {
    $str = '<div id="debugCode">';
    $str .= "&nbsp;&nbsp;debuginfo";
    $str.= '<div id="debugCodeHeader">';
    $str .= "XML RPC CALL FUNCTION: $method(";
    if (!$params) {
        $params = "null";
    } else if (is_array($params)) {
        $str .= implode (',',$params);
    } else {
        $str .= $params;
    }
    $str .=')';
    $str .= "</div>";
    if (is_array($xmlResponse)) {
        $str .= "<pre>";
        $str .= "result : ";
        $str .= var_export($xmlResponse);
        $str .= "</pre>";
    } else {
        $str .= "result : ".$xmlResponse;
    }
    $str .= '</div>';
    echo $str;
}

/* If the XML-RPC server sent a fault, display an error */
if (($xmlResponse["faultCode"])&&(is_array($xmlResponse))) {
    print($xmlResponse["faultCode"].":".$xmlResponse["faultString"]."\n");
    exit -1;
}

/* Return the result of the remote procedure call */
print_r($xmlResponse);
echo "\n";
?>

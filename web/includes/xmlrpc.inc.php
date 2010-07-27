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

require_once("ErrorHandling.php");

/**
 * Little class to encapsulate string into a XML-RPC binary string
 */
class Trans {
    var $scalar;
    var $xmlrpc_type;
}

/**
 * Return a Trans object so that a potentially non XML-safe string can be sent
 * into the XML-RPC stream.
 * e.g. a password can contains the & character, so the password string must be encoded.
 */
function prepare_string($pass) {
    $obj = new Trans();
    $obj->scalar = "$pass";
    $obj->xmlrpc_type = "base64";
    return $obj;
}

/**
 * FIXME: to remove
 * function wich decode UTF-8 Entity with ref
 * &#03; for example
 * need because XMLRPC server doest not like this sort
 * of encoding
 */
function decode_entities($text) {
    $text = html_entity_decode($text,ENT_QUOTES,"ISO-8859-1"); /* NOTE: UTF-8 does not work! */
    $text= preg_replace('/&#(\d+);/me',"chr(\\1)",$text); /* decimal notation */
    $text= preg_replace('/&#x([a-f0-9]+);/mei',"chr(0x\\1)",$text);  /* hex notation */
    return $text;
}

/**
 * Return a socket object
 */
function openSocket($proto, $conf) {
    $errLevel = error_reporting();
    error_reporting(0);
    if (($proto != "ssl://")
        || ($conf[$_SESSION["agent"]]["verifypeer"] != 1)
        || !function_exists("stream_socket_client")) {
        /*
           Not a SSL connection,
           or simple SSL connection without client certificate and server
           certificate check
           or stream_socket_client function not available (PHP 5 only),
        */
        $sock = fsockopen($proto.$_SESSION["XMLRPC_agent"]["host"], $_SESSION["XMLRPC_agent"]["port"], $errNo, $errString);
        $ret = array($sock, $errNo, $errString);
    } else {
        $context = stream_context_create();
        stream_context_set_option($context, "ssl", "allow_self_signed", False);
        stream_context_set_option($context, "ssl", "verify_peer", True);
        stream_context_set_option($context, "ssl", "cafile", $conf[$_SESSION["agent"]]["cacert"]);
        stream_context_set_option($context, "ssl", "local_cert", $conf[$_SESSION["agent"]]["localcert"]);
        $sock = stream_socket_client('tls://'.$_SESSION["XMLRPC_agent"]["host"].":".$_SESSION["XMLRPC_agent"]["port"], $errNo, $errString, ini_get("default_socket_timeout"), STREAM_CLIENT_CONNECT, $context);
        $ret = array($sock, $errNo, $errString);
    }
    error_reporting($errLevel);
    if ($sock !== False) {
        /* Setting timeout on a SSL socket only works with PHP >= 5.2.1 */
        stream_set_timeout($sock, $conf[$_SESSION["agent"]]["timeout"]);
    }
    return $ret;
}

/**
 *  @return 1 if an XMLRPC exception has been raised, else 0
 */
function isXMLRPCError() {
    global $errorStatus;
    return $errorStatus;
}

/**
 * Make a XML-RPC call
 * If the global variable $errorStatus is not zero, the XML-RPC call is not
 * done, and this function returns nothing.
 *
 * @param $method name of the method
 * @param $params array with param
 * @return the XML-RPC call result
 */
function xmlCall($method, $params = null) {
    global $errorStatus;
    global $errorDesc;
    global $conf;

    if (isXMLRPCError()) { // Don't do a XML-RPC call if a previous one failed
        return;
    }

    /*
      Set defaut login/pass if not set.
      The credentials are used to authenticate the web interface to the XML-RPC
      server.
    */
    if (!isset($conf["global"]["login"])) {
        $conf["global"]["login"] = "mmc";
        $conf["global"]["password"] = "s3cr3t";
    }

    $output_options = array( "output_type" => "xml", "verbosity" => "pretty", "escaping" => array("markup"), "version" => "xmlrpc", "encoding" => "UTF-8" );

    $request = xmlrpc_encode_request($method, $params, $output_options);

    /* We build the HTTP POST that will be sent */
    $host= $_SESSION["XMLRPC_agent"]["host"].":".$_SESSION["XMLRPC_agent"]["port"];
    $url = "/";
    $httpQuery = "POST ". $url ." HTTP/1.0\r\n";
    $httpQuery .= "User-Agent: MMC web interface\r\n";
    $httpQuery .= "Host: ". $host ."\r\n";
    $httpQuery .= "Content-Type: text/xml\r\n";
    $httpQuery .= "Content-Length: ". strlen($request) . "\r\n";
    /* Don't set the RPC session cookie if the user is on the login page */
    if ($method == "base.ldapAuth") {
        unset($_SESSION["RPCSESSION"]);
        $httpQuery .= "X-Browser-IP: " . $_SERVER["REMOTE_ADDR"] . "\r\n";
        $httpQuery .= "X-Browser-HOSTNAME: " . gethostbyaddr($_SERVER["REMOTE_ADDR"]) . "\r\n";
    } else {
        $httpQuery .= "Cookie: " . $_SESSION["RPCSESSION"] . "\r\n";
    }
    $httpQuery .= "Authorization: Basic ".base64_encode($conf["global"]["login"].":".$conf["global"]["password"]) . "\r\n\r\n";
    $httpQuery .= $request;
    $sock = null;

    /* Connect to the XML-RPC server */
    if ($_SESSION["XMLRPC_agent"]["scheme"] == "https") {
        $prot = "ssl://";
    } else {
        $prot = "";
    }

    list($sock, $errNo, $errString) = openSocket($prot, $conf);
    if (!$sock) {
        /* Connection failure */
        $errObj = new ErrorHandlingItem('');
        $errObj->setMsg(_("Can't connect to MMC agent"));
        $errObj->setAdvice(_("MMC agent seems to be down or not correctly configured.") . '<br/> Error: '. $errNo . ' - '. $errString);
        $errObj->setTraceBackDisplay(false);
        $errObj->setSize(400);
        $errObj->process('');
        $errorStatus = 1;
        return FALSE;
    }

    /* Send the HTTP POST */
    if ( !fwrite($sock, $httpQuery, strlen($httpQuery)) ) {
        /* Failure */
        $errObj = new ErrorHandlingItem('');
        $errObj->setMsg(_("Can't send XML-RPC request to MMC agent"));
        $errObj->setAdvice(_("MMC agent seems to be not correctly configured."));
        $errObj->setTraceBackDisplay(false);
        $errObj->setSize(400);
        $errObj->process('');
        $errorStatus = 1;
        return FALSE;
    }
    fflush($sock);

    /* Get the response from the server */
    $xmlResponse = '';
    while (!feof($sock)) {
        $ret = fread($sock, 8192);
        $info = stream_get_meta_data($sock);
        if ($info['timed_out']) {
            $errObj = new ErrorHandlingItem('');
            $errObj->setMsg(_('MMC agent communication problem'));
            $errObj->setAdvice(_('Timeout when reading data from the MMC agent. Please check network connectivity and server load.'));
            $errObj->setTraceBackDisplay(false);
            $errObj->setSize(400);
            $errObj->process('');
            $errorStatus = 1;
            return FALSE;
        }
        if ($ret === False) {
            $errObj = new ErrorHandlingItem('');
            $errObj->setMsg(_("Error while reading MMC agent XML-RPC response."));
            $errObj->setAdvice(_("Please check network connectivity."));
            $errObj->setTraceBackDisplay(false);
            $errObj->setSize(400);
            $errObj->process('');
            $errorStatus = 1;
            return FALSE;
        }
        $xmlResponse .= $ret;
    }
    fclose($sock);

    /* Process the response */
    if (!strlen($xmlResponse)) {
        $errObj = new ErrorHandlingItem('');
        $errObj->setMsg(_("MMC agent communication problem"));
        $errObj->setAdvice(_("Can't communicate with MMC agent. Please check you're using the right TCP port and the right protocol."));
        $errObj->setTraceBackDisplay(false);
        $errObj->setSize(400);
        $errObj->process('');
        $errorStatus = 1;
        return FALSE;
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
            $errObj = new ErrorHandlingItem('');
            $errObj->setMsg(_("MMC agent communication problem"));
            $errObj->setAdvice(_("The MMC agent didn't give us a session number. Please check the MMC agent version."));
            $errObj->setTraceBackDisplay(false);
            $errObj->setSize(400);
            $errObj->process('');
            $errorStatus = 1;
            return False;
        }
    }

    /* Process the XML response */
    $xmlResponse = substr($xmlResponse, $pos + 4);
    /*
       Test if the XMLRPC result is a boolean value set to False.
       If it is the case, xmlrpc_decode will return an empty string.
       So we need to test this special case.

       Looks like this bug is fixed in latest PHP version. At least it works
       with PHP 5.2.0.
    */
    $booleanFalse = "<?xml version='1.0'?>\n<methodResponse>\n<params>\n<param>\n<value><boolean>0</boolean></value>\n</param>\n</params>\n</methodResponse>\n";
    if ($xmlResponse == $booleanFalse) $xmlResponse = False;
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
            $str .= var_export($params, True);
        } else {
            $str .= $params;
        }
        $str .=')';
        $str .= "</div>";
        if (is_array($xmlResponse)) {
            $str .= "<pre>";
            $str .= "result : ";
            $str .= var_export($xmlResponse, True);
            $str .= "</pre>";
        } else {
            $str .= "result : ".$xmlResponse;
        }
        $str .= '</div>';
        echo $str;
    }

    /* If the XML-RPC server sent a fault, display an error */
    if ((is_array($xmlResponse) && (isset($xmlResponse["faultCode"])))) {
        if ($xmlResponse["faultCode"] == "8003") {
            /*
              Fault 8003 means the session with the XML-RPC server has expired.
              So we make the current PHP session expire, so that the user is
              redirected to the login page.
            */
            unset($_SESSION["expire"]);
            $_SESSION["agentsessionexpired"] = 1;
            $root = $conf["global"]["root"];
            header("Location: $root" . "main.php");
            exit;
        }
        /* Try to find an error handler */
        $result = findErrorHandling($xmlResponse["faultCode"]);
        if (!is_object($result) and $result == -1) {
            /* We didn't find one */
            $result = new ErrorHandlingItem('');
            $result->setMsg(_("unknown error"));
            $result->setAdvice(_("This exception is unknown. Please contact us to add an error handling on this error."));
        }
        $result->process($xmlResponse);
        $errorStatus = 1;
        $errorDesc = $xmlResponse["faultCode"];
        return False;
    }

    /* Return the result of the remote procedure call */
    return $xmlResponse;
}

/**
 * try to find an ErrorHandlingItem for $errorFaultCode
 * @see ErrorHandlingObject
 * @see ErrorHandlingItem
 */
function findErrorHandling($errorFaultCode) {
    require("includes/commonErrorHandling.php");

    if (!empty($_GET["module"])) {
        $errorfile = "modules/".$_GET["module"]."/includes/errorHandling.php";
        if (file_exists($errorfile)) {
            require($errorfile);
        }
    }

    if (isset($errObj)) { //if error obj is set
        return ($errObj->handle($errorFaultCode));
    } else {
        return -1;
    }
}

?>

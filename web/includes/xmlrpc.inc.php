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
?>
<?php

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
 * call an xmlrpc call for a method
 * via the xmlrpc server in python (lmc-agent)
 * @param $method name of the method
 * @param $params array with param
 */
function xmlCall($method, $params = null) {
        global $errorStatus;
        if ($errorStatus !=0) { //ignore XMLRPC call after one error
            return;
        }

        global $conf;

            //set defaut login/pass if not set
            if (!isset($conf["global"]["login"])) {
                $conf["global"]["login"] = "lmc";
                $conf["global"]["password"] = "s3cr3t";
            }

        $output_options = array( "output_type" => "xml", "verbosity" => "pretty", "escaping" => array("markup", "non-ascii", "non-print"), "version" => "xmlrpc", "encoding" => "UTF-8" );

        if ($params==null) {
                $request = xmlrpc_encode_request($method,null,$output_options);
        }
        else {
                $request = xmlrpc_encode_request($method,$params,$output_options);
                $request=decode_entities($request,ENT_QUOTES,"UTF-8");
        }


        $host= $_SESSION["XMLRPC_agent"]["host"].":".$_SESSION["XMLRPC_agent"]["port"];
        $url = "/";

        $httpQuery = "POST ". $url ." HTTP/1.0\r\n";
        $httpQuery .= "User-Agent: xmlrpc\r\n";
        $httpQuery .= "Host: ". $host ."\r\n";
        $httpQuery .= "Content-Type: text/xml\r\n";
        $httpQuery .= "Content-Length: ". strlen($request) ."\r\n";
        $httpQuery .= "Authorization: Basic ".base64_encode($conf["global"]["login"]).":".base64_encode($conf["global"]["password"]) . "\r\n\r\n";
        $httpQuery .= $request;
        $sock=null;

        // if crypted connexion
        if ($_SESSION["XMLRPC_agent"]["scheme"]=="https") { $prot="ssl://"; }
        $errLevel = error_reporting();
        error_reporting(0);
        $sock = fsockopen($prot.$_SESSION["XMLRPC_agent"]["host"],$_SESSION["XMLRPC_agent"]["port"], $errNo, $errString);
        error_reporting($errLevel);

        if ( !$sock ) {
                $errObj = new ErrorHandlingItem('');
                $errObj->setMsg(_("lmc-agent not responding"));
                $errObj->setAdvice(_("LMC-Agent seems to be down or not correctly configured.".'<br/> Error: '. $errNo . ' - '. $errString));
                $errObj->setTraceBackDisplay(false);
                $errObj->setSize(400);
                $errObj->process('');

                $errorStatus = 1;

                return FALSE;
        }
        if ( !fwrite($sock, $httpQuery, strlen($httpQuery)) ) {
                echo 'Error while trying to send request';
                return FALSE;
        }
        fflush($sock);
        // We get the response from the server
        while ( !feof($sock) ) {
                $xmlResponse .= fgets($sock);
        }
        // Closing the connection
        fclose($sock);
    	$xmlResponse = substr($xmlResponse, strpos($xmlResponse, "\r\n\r\n") +4);
	/*****
         * To decode the XML into PHP, we use the (finaly a short function)
         * xmlrpc_decode function. And that should've done the trick.
         * We now have what ever the server function made in our $xmlResponse
         * variable.
         *****/

        /* Test if the XMLRPC result is a boolean value set to False.
           If it is the case, xmlrpc_decode will return an empty string.
	   So we need to test this special case. */

	$booleanFalse = "<?xml version='1.0'?>\n<methodResponse>\n<params>\n<param>\n<value><boolean>0</boolean></value>\n</param>\n</params>\n</methodResponse>\n";
	if ($xmlResponse == $booleanFalse) $xmlResponse = "0";
	else {
                $xmlResponseTmp = xmlrpc_decode($xmlResponse,"UTF-8");

                //if we cannot decode in UTF-8
                if (!$xmlResponseTmp) {
                        //conversion in UTF-8
                        $xmlResponse = iconv("ISO-8859-1","UTF-8",$xmlResponse);
                        $xmlResponse = xmlrpc_decode($xmlResponse,"UTF-8");
                } else {
                        $xmlResponse=$xmlResponseTmp;
                }
	}

        /*
         * When debug is on
         */
        global $conf;
        if ($conf["debug"]["level"]!=0) {
                $str = '<div id="debugCode">';
                $str .= "&nbsp;&nbsp;debuginfo";
                $str.= '<div id="debugCodeHeader">';
                $str .= "XML RPC CALL FUNCTION: $method(";
                if (!$params)
                {
                        $params="null";
                }
                if (is_array($params)) {
                        $str.= implode (',',$params);
                }

                else
                {
                        $str.= $params;
                }
                $str.=')';
                $str.= "</div>";

                if (is_array($xmlResponse)) {
                        $str.= "<pre>";
                        $str.= "result : ";
                        $str.= var_export($xmlResponse);
                        $str.= "</pre>";
                }
                else
                {
                        $str.= "result : ".$xmlResponse;
                }
                $str.= '</div>';

                echo $str;
        }

        /*
         *  fin de cas de debug
         */

        /*
         * if error
         */
        if (($xmlResponse["faultCode"])&&(is_array($xmlResponse))) {
                $result = findErrorHandling($xmlResponse["faultCode"]); //try to find an error handler

                if ($result==-1) { //if we not find an error handler
                    $result = new ErrorHandlingItem('');
                    $result->setMsg(_("unknown error"));
                    $result->setAdvice(_("This exception is unknow. Please contact us to add an error handling on this error."));
                }

                $result->process($xmlResponse);

                $errorStatus = 1;
                global $errorDesc;
                $errorDesc = $xmlResponse["faultCode"];

                //cleanup $xmlresponse var
                unset ($xmlResponse["faultCode"]);
                unset ($xmlResponse["faultString"]);
                unset ($xmlResponse["faultTraceback"]);
                return array();
        }
        /*
         * end error handling
         */

        return $xmlResponse;

}

/**
 *  return if an XMLRPC exception has been raised
 */
function isXMLRPCError() {
    global $errorStatus;
    return $errorStatus;
}

/**
 * log a line into agent log
 */
function agentLog($logline) {
    $path = $_GET['module'].'/'.$_GET['submod'].'/'.$_GET['action'];
    return xmlCall("log",array($_SERVER['SERVER_ADDR'],"PATH: $path\n".$logline."\n"));
}

/**
 * remote execution of a command line
 */
function remote_exec($cmd,&$ret) {
        $ret = xmlCall("base.launch",$cmd);
        return $ret;
}

/**
 * try to find an ErrorHandlingItem for $errorFaultCode
 * @see ErrorHandlingObject
 * @see ErrorHandlingItem
 */
function findErrorHandling($errorFaultCode) {
    $errorfile = "modules/".$_GET["module"]."/includes/errorHandling.php";

    require("includes/commonErrorHandling.php");
    if (file_exists($errorfile)) {
        require($errorfile);
    }

    if (isset($errObj)) { //if error obj is set
        return ($errObj->handle($errorFaultCode));
    } else {
        return -1;
    }
}

?>

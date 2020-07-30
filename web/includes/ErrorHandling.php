<?php
/*
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

/**
 * class which handle error message
 */
class ErrorHandlingItem {
    var $msg;
    var $advice;
    var $regexp;
    var $regs; /**< matched value in regexp */

    var $_size;
    var $_level;
    var $_showTraceBack;

    function ErrorHandlingItem($regexp) {
        $this->regexp = '#'.$regexp.'#';
        $this->msgRegExp = false;
        $this->_size = 800; //default notify Widget size
        $this->_level = 4; //default ErrorHandling level
        $this->_showTraceBack = true; //show traceBack
    }

    function setTraceBackDisplay($bool) {
        $this->_showTraceBack=$bool;
    }

    function setLevel($lvl) {
        $this->_level = $lvl;
    }

    function setSize($size) {
        $this->_size = $size;
    }

    function process($xmlResponse) {
        $this->registerNotify($xmlResponse);
    }

    /**
     * Prepare error message to display
     */
    function registerNotify($xmlResponse) {
        if ($this->_level !=0 ) {
            $str= '<div class="alert alert-error">';
        } else {
            $str = '<div class="alert alert-info">';
        }

        $str .= "<h1>" . $this->getMsg() . "</h1>";
        if ($this->getAdvice())
            $str .= "<p>" . $this->getAdvice() . "</p>";;

        if ($this->_showTraceBack) {

            $copied_message = _("Copied");
            $selector = "jQuery(this).parent().find('.errorTraceback')";
            $script = "var textareaToRemove = jQuery( '<textarea>' );
            jQuery( 'body' ).append(textareaToRemove);
            jQuery(textareaToRemove).val(jQuery(this).parent().find('pre').text()).select();
            document.execCommand( 'copy' );
            jQuery(textareaToRemove).remove();
            console.log(jQuery(this).text('$copied_message'));";

            $str .= '<a class="btn btn-danger" href="#" onclick="jQuery(this).parent().find('.$selector.').toggle();">'._("Show complete trackback").'</a>';
            $str .= '<a class="btn" href="#" onclick="'.$script.'">'._("Copy to clipboard").'</a>';
            $str .= '<div class="errorTraceback" style="display:none;"><h1>'._("Complete Traceback").'</h1><pre>';
            $str .= gmdate("d M Y H:i:s") . "\n\n";
            $str .= "PHP XMLRPC call: " . $xmlResponse["faultString"] . "\n\n";
            $str .= "Python Server traceback:\n";
            $str .= htmlentities($xmlResponse["faultTraceback"])."\n";
            $str .= '</pre></div>';
        }
        $str .= '</div>';

        $logstr = "PHP XMLRPC error: ".$xmlResponse["faultString"].' at '.gmdate("d M Y H:i:s")."\n\n";
        $logstr .= "Python Server traceback: \n";
        $logstr .= htmlentities($xmlResponse["faultTraceback"])."\n";
        $ret =error_log($logstr);

        $n = new NotifyWidget();
        $n->size = $this->_size;
        $n->level = $this->_level;
        $n->add($str);
    }

    function setMsg($msg) {
        $this->msg = $msg;
    }

    function setMsgFromError($regexp) {
        $this->msgRegExp = $regexp;
    }

    function setAdvice($adv) {
        $this->advice = $adv;
    }

    function match($errorMsg) {
        return preg_match($this->regexp, $errorMsg, $this->regs);
    }

    function getMsg() {
        return $this->msg;
    }

    function getAdvice() {
        return $this->advice;
    }
}

class ErrorHandlingControler{
    var $eiList;
    function ErrorHandlingControler() {
        $this->eiList = array();
    }

    function add($eiObj) {
        $this->eiList[] = $eiObj;
    }

    function handle($errormsg) {
        foreach ($this->eiList as $errorItem) {
            if ($errorItem->match($errormsg)) {
                if ($errorItem->msgRegExp) {
                    preg_match($errorItem->msgRegExp, $errormsg, $matches);
                    if (isset($matches[1])) {
                        $msg = preg_replace("/[0-9]+/", "%s", $matches[1]);
                        preg_match("/[0-9]+/", $matches[1], $nb);
                        if (isset($nb[0]))
                            $errorItem->setMsg(sprintf(_($msg), $nb[0]));
                        else
                            $errorItem->setMsg(_($msg));
                    }
                }
                return $errorItem;
            }
        }
        return -1;
    }
}

?>

<?php

/**
 * class who handle error message
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
        $this->regexp = $regexp;
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

    function registerNotify($xmlResponse) {

                if ($this->_level !=0 ) {
                    $str= '<div id="errorCode">';
                } else {
                    $str = '<div>';
                }

                $str.= "<h3>".$this->getMsg()."</h3>";
                $str.= "<p>".$this->getAdvice()."</p>";;

                if ($this->_showTraceBack) {
                    $str.= '<a href="#" onClick="Effect.toggle(\'errorTraceback\',\'slide\');">'._("Show complete trackback").'</a>';
                    $str.= '<div id="errorTraceback" style="display:none;"><h1 style="margin-top: 1em; margin-bottom: 0.2em;">'._("Complete Traceback").'</h1><pre>';
                    $str.= $xmlResponse["faultTraceback"]."\n".htmlentities($xmlResponse["faultCode"]);
                    $str.= '</pre></div>';
                }

                $str.='</div>';

		$n = new NotifyWidget();
                $n->setSize($this->_size);
                $n->setLevel($this->_level);
		$n->add($str);
    }

    function setMsg($msg) {
    $this->msg = $msg;
    }

    function setAdvice($adv) {
    $this->advice = $adv;
    }

    function match($errorMsg) {
        return ereg($this->regexp,$errorMsg,$this->regs);
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
                return $errorItem;
            }
        }
        return -1;
    }
}

?>
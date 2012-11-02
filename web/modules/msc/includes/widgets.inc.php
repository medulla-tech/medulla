<?
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
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

function msg_err_qa($msg) {
    $msgs = array(
        "Quick action path don't exists" => sprintf(_T("Quick action path %s don't exists", "msc"), $msg[2])
    );
    return $msgs[$msg[1]];
}

/* mark this string for translation */
_T("Other/N.A.", "msc");

/* HTML display for known MSC host */
class RenderedMSCHost extends RenderedLabel {
    function RenderedMSCHost($machine) {
        $this->hostname = $machine->hostname;
        $this->machine = $machine;
        $this->platform = $machine->platform;
        $this->uuid = $machine->uuid;
        $this->level = 3;
        $this->text = sprintf(_T('%s status', 'msc'), $machine->hostname);
    }

    function line($label, $text) { # FIXME: should use CSS instead of hard coded styles
        return "<tr> <th style='text-align: left' nowrap>$label :</th> <td style='width: 90%'>$text</td> </tr>";
    }

    function ajaxDisplay() {
        $buffer = '
            <script type="text/javascript">
            new Ajax.Updater("ping", "'     . urlStrRedirect("base/computers/ajaxPingProbe"). "&hostname=" . $this->hostname . '&uuid='. $this->uuid .'", { method: "get" });
            </script>
        ';
        $this->text .= ' <span id="ping"><img src="img/common/loader_p.gif" /></span>';
        print $buffer;
        $this->display();
    }
}

/* HTML display for UNknown MSC host */
class RenderedMSCGroupDontExists extends HtmlElement {
    function RenderedMSCGroupDontExists($name) {
        $this->name = $name;
        $this->str = sprintf(_T('group "%s" is not defined in the MSC module, or you don\'t have permissions to access it', 'msc'), $this->name);
    }
    function display() {
        $this->headerDisplay();
    }
    function headerDisplay() {
        $buffer = '<div class="indent"><table>';
        $buffer .= '<tr><td><span style="color:red;">';
        $buffer .= $this->str;
        $buffer .= '</span></td></tr>';
        $buffer .= '</table></div>';
        print $buffer;
    }
}

class RenderedMSCHostDontExists extends HtmlElement {
    function RenderedMSCHostDontExists($name) {
        $this->name = $name;
        $this->str = sprintf(_T('%s host is not defined in the MSC module, or you don\'t have permissions to access it', 'msc'), $this->name);
    }
    function display() {
        $this->headerDisplay();
    }
    function headerDisplay() {
        $buffer = '<div class="indent"><table>';
        $buffer .= '<tr><td><span style="color:red;">';
        $buffer .= $this->str;
        $buffer .= '</span></td></tr>';
        $buffer .= '</table></div>';
        print $buffer;
    }
}

class RenderedMSCCommandDontExists extends RenderedMSCHostDontExists {
    function RenderedMSCCommandDontExists() {
        $this->str = _T("You don't have the right permissions to display this command", "msc");
    }
}

class RedirectMSC extends HtmlElement {
    function RedirectMSC($dest) {
        print "<html><head><meta http-equiv=\"refresh\" content=\"0;url=$dest\"></head></html>";
        exit();
    }
}

/* top label, with nav links */
class RenderedLabel extends HtmlElement {
    function RenderedLabel($level, $text) {
        $this->level = $level;
        $this->text = $text;
    }

    function display() {
        print "<h$this->level>$this->text</h$this->level>";
    }
}

/* Quick actions dropdown list */
class RenderedMSCActions extends HtmlElement {

    function RenderedMSCActions($script_list, $qa_on_name, $params) {
        $this->list = array();
        $this->qa_on_name = $qa_on_name;
        $this->params = $params;
        $this->name = "mscactions";
        $this->url = $_SERVER["REQUEST_URI"];
        $this->module = "base";
        $this->submod = "computers";
        $this->action = "start_quick_action";
        $this->enabled = hasCorrectAcl("base", "computers", "start_quick_action");

        $this->error = !$script_list[0];
        if (!$this->error) {
            foreach ($script_list[1] as $script) {
                array_push($this->list, new RenderedMSCAction($script));
            }
        } else {
            $this->errmsg = msg_err_qa($script_list);
        }
    }

    function display() {
        if (!$this->enabled) {
            $selectDisabled = "DISABLED";
            $onSubmit = "";
        } elseif (!$this->error) {
            $selectDisabled = "";
            $onSubmit = 'onsubmit="showPopup(event,\'' . urlStrRedirect($this->module . "/" . $this->submod . "/" . $this->action, $this->params) . '&launchAction=\' + $(\'launchAction\').value); return false;"';
        } else {
            $selectDisabled = "DISABLED";
            $onSubmit = "";
        }

        if (!$this->error && count($this->list) > 0) {
            $label = new RenderedLabel(3, sprintf(_T('Quick action on %s', 'msc'), $this->qa_on_name));
            $label->display();

?>
    <script type="text/javascript">
            document.observe("dom:loaded", function() { 
                var inputImg = $('launchActionImg');
                var src = inputImg.src;
                var style = inputImg.style;

                var inputImgInactive= new Element("img", {src: src, style: style, id: "launchActionImg"});
                var inputImgActive= new Element("input", {src: src, style: style, type: "image", id: "launchActionImg"});
                
                inputImg.replace(inputImgInactive.setOpacity(0.3));

                $('launchAction').observe('change', function() {
                    if ($('launchAction').selectedIndex == 0) {
                        $('launchActionImg').replace(inputImgInactive.setOpacity(0.3));
                    }
                    else {
                        $('launchActionImg').replace(inputImgActive);
                    }
                });
            });
</script>
<?php

            print '
                <div id="msc-standard-host-actions"> <!-- STANDARD HOST ACTIONS -->
                    <table>
                        <tr>
                        <td>
                            <form ' . $onSubmit . ' name="' . $this->name . '" id="'.$this->name . '">
                            <select name="launchAction" id="launchAction" style="border: 1px solid grey;" ' . $selectDisabled . '>
                                <option value="">'._T('Execute action...', 'msc').'</option>';
            foreach ($this->list as $script) {
                $script->display();
            }
            print '</select>';
            $img = new RenderedImgInput('/mmc/modules/msc/graph/images/button_ok.png');
            if ($this->enabled) {
                $img->display();
            } else {
                $img->displayWithNoRight();
            }
            print '
                            </form>
                        </td>
                        </tr>
                    </table>
                </div>';
        } elseif (!$this->error) {
            print '
                <div id="msc-standard-host-actions"> <!-- STANDARD HOST ACTIONS -->
                    <table>
                        <tr>
                        <td>
                            '._T('Quick action list is empty', 'msc').'
                        </td>
                        </tr>
                    </table>
                </div>';
        } else {
            print '
                <div id="msc-standard-host-actions"> <!-- STANDARD HOST ACTIONS -->
                    <table>
                        <tr>
                        <td>
                            '.$this->errmsg.'
                        </td>
                        </tr>
                    </table>
                </div>';
        }
    }
}

/* Quick action element */
class RenderedMSCAction extends HtmlElement {
    function RenderedMSCAction($script) {
        $this->filename = $script['filename'];
        /* Try to find a localized version of the quick action title */
        if (!empty($script['title' . $_SESSION['lang']])) {
            $this->title = $script['title' . $_SESSION['lang']];
        } else if ((strlen($_SESSION['lang']) == 5) && !empty($script['title' . substr($_SESSION['lang'], 0, 2)])) {
            $this->title = $script['title' . substr($_SESSION['lang'], 0, 2)];
        } else {
            /* Use the default English title */
            $this->title = $script['title'];
        }
    }

    function display() {
        print '<option value="'.$this->filename.'">'.$this->title.'</option>';
    }
}

class RenderedImgInput extends HtmlElement {
    function RenderedImgInput($path, $style = '') {
        $this->path = $path;
        $this->style = $style;
    }

    function display() {
        print '
             <input
                id="launchActionImg"
                type="image"
                src="'.$this->path.'"
                style="'.$this->style.'"
            />';
    }

    function displayWithNoRight() {
        print '
             <img
                src="'.$this->path.'"
                style="'.$this->style.';opacity: 0.30;"
            />';
    }
}

class AjaxFilterCommands extends AjaxFilter {

    function AjaxFilterCommands($url, $divid = "container", $paramname = 'commands', $params = array()) {
        $this->AjaxFilter($url, $divid, $params);
        $this->commands = new SelectItem($paramname, 'pushSearch', 'searchfieldreal noborder');
        $this->paramname = $paramname;
        $elts = array("mine" => _T("My commands", "msc"), "all" => _T("All users commands", "msc"));
        $this->setElements($elts);
        $this->setElementsVal(array("mine" => "mine", "all" => "all"));
        if (isset($_SESSION["msc_commands_filter"])) {
            $this->setSelected($_SESSION["msc_commands_filter"]);
        } else {
            $this->setSelected(getCommandsFilter());
        }
    }

    function setElements($elt) {
        $this->commands->setElements($elt);
    }

    function setElementsVal($elt) {
        $this->commands->setElementsVal($elt);
    }

    function setSelected($elemnt) {
        $this->commands->setSelected($elemnt);
    }

    function display() {
        global $conf;
        $root = $conf["global"]["root"];

?>
<form name="Form" id="Form" action="#">

    <div id="loader"><img id="loadimg" src="<?php echo $root; ?>img/common/loader.gif" alt="loader" class="loader"/></div>

    <div id="searchSpan" class="searchbox" style="float: right;">
    <img src="graph/search.gif" style="position:relative; top: 2px; float: left;" alt="search" />

    <span class="searchfield">
<?php
        $this->commands->display();
?>
    </span>&nbsp;

    <span class="searchfield"><input type="text" class="searchfieldreal" name="param" id="param" onkeyup="pushSearch(); return false;" />
    <img src="graph/croix.gif" alt="suppression" style="position:relative; top : 3px;"
    onclick="document.getElementById('param').value =''; pushSearch(); return false;" />
    </span>
    </div>

    <script type="text/javascript">
        document.getElementById('param').focus();
        var refreshtimer = null;
        var refreshparamtimer = null;
        var refreshdelay = <?php echo  $this->refresh ?>;

<?
if(isset($this->storedfilter)) {
?>
        document.Form<?php echo $this->formid ?>.param.value = "<?php echo $this->storedfilter ?>";
<?
}    
?>
        /**
         * Clear the timers set vith setTimeout
         */
        function clearTimers() {
            if (refreshtimer != null) {
                clearTimeout(refreshtimer);
            }
            if (refreshparamtimer != null) {
                clearTimeout(refreshparamtimer);
            }
        }

        /**
         * Update div
         */
        function updateSearch() {
            new Ajax.Updater('<?php echo  $this->divid; ?>','<?php echo  $this->url; ?>filter='+document.Form.param.value+'<?php echo  $this->params ?>&<?php echo  $this->paramname ?>='+document.Form.<?php echo  $this->paramname ?>.value, { asynchronous:true, evalScripts: true});

<?
if ($this->refresh) {
?>
            refreshtimer = setTimeout("updateSearch()", refreshdelay)
<?
}
?>
        }

        /**
         * Update div when clicking previous / next
         */
        function updateSearchParam(filter, start, end) {
            clearTimers();
            new Ajax.Updater('<?php echo  $this->divid; ?>','<?php echo  $this->url; ?>filter='+filter+'<?php echo  $this->params ?>&<?php echo  $this->paramname ?>='+document.Form.<?php echo  $this->paramname ?>.value+'&start='+start+'&end='+end, { asynchronous:true, evalScripts: true});

<?
if ($this->refresh) {
?>
            refreshparamtimer = setTimeout("updateSearchParam('"+filter+"',"+start+","+end+")", refreshdelay);
<?
}
?>
        }

        /**
         * wait 500ms and update search
         */
        function pushSearch() {
            clearTimers();
            refreshtimer = setTimeout("updateSearch()", 500);
        }

        pushSearch();
    </script>

</form>
<?
          }
}

class AjaxFilterCommandsStates extends AjaxFilter {

    function AjaxFilterCommandsStates($url, $divid = "container", $paramname1 = 'commands', $paramname2 = 'currentstate', $params = array()) {
        $this->AjaxFilter($url, $divid, $params);

        /* Commands selection dropdown */
        $this->commands = new SelectItem($paramname1, 'pushSearch', 'searchfieldreal noborder');
        $this->paramname1 = $paramname1;
        $elts = array("mine" => _T("My commands", "msc"), "all" => _T("All users commands", "msc"));
        $this->commands->setElements($elts);
        $this->commands->setElementsVal(array("mine" => "mine", "all" => "all"));
        if (isset($_SESSION["msc_commands_filter"])) {
            $this->commands->setSelected($_SESSION["msc_commands_filter"]);
        } else {
            $this->commands->setSelected(getCommandsFilter());
        }

        /* State selection dropdown */
        $this->paramname2 = $paramname2;
        $this->states = new SelectItem($paramname2, 'pushSearch2', 'searchfieldreal noborder');
    }

    function setElements($elt) {
        $this->states->setElements($elt);
    }

    function setElementsVal($elt) {
        $this->states->setElementsVal($elt);
    }

    function setSelected($elemnt) {
        $this->states->setSelected($elemnt);
    }

    function display() {
        global $conf;
        $root = $conf["global"]["root"];

?>
<form name="Form" id="Form" action="#">

    <div id="loader"><img id="loadimg" src="<?php echo $root; ?>img/common/loader.gif" alt="loader" class="loader"/></div>

    <div id="searchSpan" class="searchbox" style="float: right;">
    <img src="graph/search.gif" style="position:relative; top: 2px; float: left;" alt="search" />

    <span class="searchfield">
<?php
        $this->commands->display();
        $this->states->display();
?>
    </span>&nbsp;

    <span class="searchfield"><input type="text" class="searchfieldreal" name="param" id="param" onkeyup="pushSearch(); return false;" />
    <img src="graph/croix.gif" alt="suppression" style="position:relative; top : 3px;"
    onclick="document.getElementById('param').value =''; pushSearch(); return false;" />
    </span>
    </div>

    <script type="text/javascript">
        document.getElementById('param').focus();
        var refreshtimer = null;
        var refreshparamtimer = null;
        var refreshdelay = <?php echo  $this->refresh ?>;

<?
if(isset($this->storedfilter)) {
?>
        document.Form<?php echo $this->formid ?>.param.value = "<?php echo $this->storedfilter ?>";
<?
}    
?>
        /**
         * Clear the timers set vith setTimeout
         */
        function clearTimers() {
            if (refreshtimer != null) {
                clearTimeout(refreshtimer);
            }
            if (refreshparamtimer != null) {
                clearTimeout(refreshparamtimer);
            }
        }

        /**
         * Update div
         */
        function updateSearch() {
            clearTimers();
            new Ajax.Updater('<?php echo  $this->divid; ?>','<?php echo  $this->url; ?>filter='+document.Form.param.value+'<?php echo  $this->params ?>&<?php echo  $this->paramname1 ?>='+document.Form.<?php echo  $this->paramname1 ?>.value+'&<?php echo  $this->paramname2 ?>='+document.Form.<?php echo  $this->paramname2 ?>.value, { asynchronous:true, evalScripts: true});

<?
if ($this->refresh) {
?>
            refreshtimer = setTimeout("updateSearch()", refreshdelay)
<?
}
?>
        }

        /**
         *
         */
        function updateStates() {
            var ind = document.getElementById('<?php echo  $this->paramname2; ?>');
            var val = ind.options[ind.selectedIndex].value;
            new Ajax.Updater('<?php echo  $this->paramname2; ?>', '<?php echo  urlStrRedirect('msc/logs/state_list', array('paramname2'=>$this->paramname2)); ?>&<?php echo  $this->paramname1 ?>='+document.Form.<?php echo  $this->paramname1 ?>.value+'&selected='+document.Form.<?php echo  $this->paramname2 ?>.value, {asynchronous:true, evalScripts: true });
            refreshtimer = setTimeout("updateSearch()", 500);
        }

        /**
         * Update div when clicking previous / next
         */
        function updateSearchParam(filter, start, end) {
            clearTimers();
            new Ajax.Updater('<?php echo  $this->divid; ?>','<?php echo  $this->url; ?>filter='+filter+'<?php echo  $this->params ?>&<?php echo  $this->paramname1 ?>='+document.Form.<?php echo  $this->paramname1 ?>.value+'&<?php echo  $this->paramname2 ?>='+document.Form.<?php echo  $this->paramname2 ?>.value+'&start='+start+'&end='+end, { asynchronous:true, evalScripts: true});

<?
if ($this->refresh) {
?>
            refreshparamtimer = setTimeout("updateSearchParam('"+filter+"',"+start+","+end+")", refreshdelay);
<?
}
?>
        }

        /**
         * wait 500ms and update search
         */
        function pushSearch2() {
            clearTimers();
            refreshtimer = setTimeout("updateSearch()", 750);
        }

        function pushSearch() {
            clearTimers();
            setTimeout("updateStates()", 100);
        }

        pushSearch2();
    </script>

</form>
<?
          }

}

?>

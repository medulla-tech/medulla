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
        $this->str = _T("You don't have the good permissions to access this command");
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
            $img = new RenderedImgInput('/mmc/modules/msc/graph/images/button_ok.png', $buttonStyle);
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
        $this->title = $script['title'];
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

?>

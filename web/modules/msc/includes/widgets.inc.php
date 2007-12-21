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

class RenderedMSCHost extends HtmlElement {
    function RenderedMSCHost($machine) {
        $this->hostname = $machine->hostname;
        $this->machine = $machine;
        $this->platform = $machine->platform;
        $this->ping = ($machine->ping ? _("success") : _("failed"));
    }

    function line($label, $text) { # FIXME: should use CSS instead of hard coded styles
        return "<tr> <th style='text-align: left' nowrap>$label :</th> <td style='width: 90%'>$text</td> </tr>";
    }

/*    function display() {
        $buffer =
            '<div class="indent">'.
                '<table class="vertical">'.
                    '<tbody>';
        $buffer .= $this->line(_('Host name'), $this->hostname);
        $buffer .= $this->line(_('IP address'), $this->ip);
        if (strlen($this->profile) > 0)
            $buffer .= $this->line(_('Belongs to profile'), '<a href="'.$this->script_profile.'">'.$this->profile.'</a>');
        else
            $buffer .= $this->line(_('Belongs to profile'), '&nbsp;');
        if (strlen($this->group) > 0)
            $buffer .= $this->line(_('Belongs to group'), '<a href="'.$this->script_group.'">'.$this->group.'</a>');
        else
            $buffer .= $this->line(_('Belongs to group'), '&nbsp;');

        if ($this->session->ping_error) {
            $buffer .= $this->line(_('Ping'), _('failed'));
            $buffer .= $this->line(_('SSH connection'), _('not_tested'));
            $buffer .= $this->line(_('Autofs mount'), _('not_tested'));
        } elseif ($this->session->error_ssh_failed) {
            $buffer .= $this->line(_('Ping'), _('success'));
            $buffer .= $this->line(_('SSH connection'), _('failed'));
            $buffer .= $this->line(_('SSH command'), $this->session->ssh_test_command);
            $buffer .= $this->line(_('SSH return value'), $this->session->ssh_return_var);
            if (is_array($this->session->ssh_array_output)) {
                $buffer .= $this->line(_('SSH output'), implode("<br/>", $this->session->ssh_array_output));
            } else {
                $buffer .= $this->line(_('SSH output'), $this->session->ssh_array_output);
            }
            $buffer .= $this->line(_('Autofs mount'), _('not_tested'));
        } elseif ($this->session->error_autofs_failed) {
            $buffer .= $this->line(_('Ping'), _('success'));
            $buffer .= $this->line(_('SSH connection'), _('success'));
            $buffer .= $this->line(_('Autofs mount'), _('failed'));
        } else {
            $buffer .= $this->line(_('Operating system'), $this->platform);
            $buffer .= $this->line(_('Ping host'), $this->ping);
        }
        $buffer .=
                    '</tbody>'.
                '</table>'.
            '</div>';
        print $buffer;
    }*/
    function headerDisplay() {
        $buffer = '<div class="indent"><table>';
        $buffer .= '<tr><td>'.$this->ip.'</td><td>'.$this->mac.'</td>';
        $buffer .= '<td>'._('Running on').' : '.$this->platform.'</td>';
        $buffer .= '<td>' . _('Ping status').' : ' . $this->ping . '</td>';
        $buffer .= '</tr>';
        $buffer .= '</table></div>';
        print $buffer;
    }
}
class RenderedMSCHostDontExists extends HtmlElement {
    function RenderedMSCHostDontExists($name) {
        $this->name = $name;
    }
    function display() {
        headerDisplay();
    }
    function headerDisplay() {
        $buffer = '<div class="indent"><table>';
        $buffer .= '<tr><td><span style="color:red;">';
        $buffer .= sprintf(_T('%s host is not defined in the MSC module', 'msc'), $this->name);
        $buffer .= '</span></td></tr>';
        $buffer .= '</table></div>';
        print $buffer;
    }
}

class RedirectMSC extends HtmlElement {
    function RedirectMSC($dest) {
        print "<html><head><meta http-equiv=\"refresh\" content=\"0;url=$dest\"></head></html>";
        exit();
    }
}

class RenderedLabel extends HtmlElement {
    function RenderedLabel($level, $text) {
        $this->level = $level;
        $this->text = $text;
    }

    function display() {
        print "<h$this->level>$this->text</h$this->level>";
    }
}

class RenderedMSCActions extends HtmlElement {
    function RenderedMSCActions($script_list, $name = 'MSCActions') {
        $this->list = array();
        $this->name = $name;
        foreach ($script_list as $script) {
            array_push($this->list, new RenderedMSCAction($script));
        }
    }

    function display() {
        print '
            <div id="msc-standard-host-actions"> <!-- STANDARD HOST ACTIONS -->
                <table>
                    <tr>
                    <td>
                        <form method="post" action="'.$this->url.'" name="'.$this->name.'" id="'.$this->name.'">
                        <select name="launchAction">
                            <option value="">'._T('Execute action...', 'msc').'</option>';
        foreach ($this->list as $script) {
            $script->display();
        }
        print '</select>';

        $img = new RenderedImgInput('/mmc/modules/msc/graph/images/button_ok.png', 'vertical-align:bottom;border:0');
        $img->display();
        print '
                        </form>
                    </td>
                    </tr>
                </table>
            </div>';
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
}

class RenderedMSCAction extends HtmlElement {
    function RenderedMSCAction($script) {
        $this->filename = $script['filename'];
        $this->title = $script['title'];
    }

    function display() {
        print '<option value="'.$this->filename.'">'.$this->title.'</option>';
    }
}





?>

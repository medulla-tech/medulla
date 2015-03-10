<?php
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

    function RenderedMSCHost($machine, $probe_order) {
        $this->hostname = $machine->hostname;
        $this->machine = $machine;
        $this->platform = $machine->platform;
        $this->uuid = $machine->uuid;
        $this->level = 3;
        $this->text = sprintf(_T('%s status', 'msc'), $machine->hostname);
        $this->probe_order = $probe_order;
    }

    function line($label, $text) { # FIXME: should use CSS instead of hard coded styles
        return "<tr> <th style='text-align: left' nowrap>$label :</th> <td style='width: 90%'>$text</td> </tr>";
    }

    function ajaxDisplay() {
        $buffer = '
            <script type="text/javascript">
            jQuery(function(){
                jQuery("#ping").load("' . urlStrRedirect("base/computers/ajaxPingProbe") . "&hostname=" . $this->hostname . "&probe_order=" . $this->probe_order . '&uuid=' . $this->uuid . '");
            });
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
            $onSubmit = 'onsubmit="showQAPopup(event,\'' . urlStrRedirect($this->module . "/" . $this->submod . "/" . $this->action, $this->params) . '&launchAction=\' + jQuery(\'#launchAction\').val()); return false;"';
        } else {
            $selectDisabled = "DISABLED";
            $onSubmit = "";
        }

        if (!$this->error && count($this->list) > 0) {
            $label = new RenderedLabel(3, sprintf(_T('Quick action on %s', 'msc'), $this->qa_on_name));
            $label->display();
            ?>
            <script type="text/javascript">
                /* ==> NOT USED
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
                 */

                jQuery(function() {
                    //jQuery('#launchActionImg')

                    jQuery('#launchActionImg').attr('src', 'modules/msc/graph/images/status/success.png').hide();

                    jQuery('#launchAction').change(function() {
                        if (jQuery(this).val() == '')
                            jQuery('#launchActionImg').hide();
                        else
                            jQuery('#launchActionImg').show();
                    });

                });
            </script>
            <?php
            print '
                <div id="msc-standard-host-actions"> <!-- STANDARD HOST ACTIONS -->
                    <table>
                        <tr>
                        <td>
                            <form ' . $onSubmit . ' name="' . $this->name . '" id="' . $this->name . '">
                            <select name="launchAction" id="launchAction" style="border: 1px solid grey;" ' . $selectDisabled . '>
                                <option value="">' . _T('Execute action...', 'msc') . '</option>';
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
                            ' . _T('Quick action list is empty', 'msc') . '
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
                            ' . $this->errmsg . '
                        </td>
                        </tr>
                    </table>
                </div>';
        }
        ?>
        <script text="text/javascript">
            function showQAPopup(evt, url) {
                PopupWindow(evt, url, 300, function(evt) {
                    jQuery('#popup').css({
                        'left': '210px',
                        'top': '280px'
                    });
                    jQuery("#overlay").fadeIn();
                });
            }
        </script>
        <?php
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
        print '<option value="' . $this->filename . '">' . $this->title . '</option>';
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
                src="' . $this->path . '"
                style="' . $this->style . '"
            />';
    }

    function displayWithNoRight() {
        print '
             <img
                src="' . $this->path . '"
                style="' . $this->style . ';opacity: 0.30;"
            />';
    }

}

class AjaxFilterCommands extends AjaxFilter {

    function AjaxFilterCommands($url, $divid = "container", $paramname = 'commands', $params = array(), $formid = 'Form') {
        $this->AjaxFilter($url, $divid, $params, $formid);
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
        <form name="Form" id="<?php print $this->formid; ?>" action="#" onsubmit="return false;">
            <div id="loader"><img id="loadimg" src="<?php echo $root; ?>img/common/loader.gif" alt="loader" class="loader"/></div>
            <div id="searchSpan" class="searchbox" style="float: right;">
            <div id="searchBest">
                <span class="searchfield"><input type="text" class="searchfieldreal" name="param" id="param" onkeyup="pushSearch<?php echo $this->divid; ?>();
                        return false;" />
                    <img src="graph/croix.gif" alt="suppression" style="position:relative; top : 3px;"
                         onclick="document.getElementById('param').value = '';
                                 pushSearch<?php echo $this->divid; ?>();
                                 return false;" />
                </span>
                <?php if (isset($_GET['cmd_id'], $_GET['gid']) && !(isset($_GET['bundle_id']) && $_GET['bundle_id'])) { ?>
                    <!-- <form id="cbx_form"> -->
                    <span class="searchfield">
                        <br/>
                        <br/>
                        <label style="padding: 7px 10px; position: relative; float: left"><b><?php print(_T('State filter', 'msc')); ?>:</b></label>
                        <input type="checkbox" name="cbx_state[]" id="cbx_done" value="done" style="top: 2px; left: 5px; position: relative; float: left" />
                        <label for="cbx_done" style="padding: 7px 10px; position: relative; float: left"><?php print(_T('Done', 'msc')); ?></label>
                        <input type="checkbox" name="cbx_state[]" id="cbx_failed" value="failed" style="top: 2px; left: 5px; position: relative; float: left" />
                        <label for="cbx_failed" style="padding: 7px 10px; position: relative; float: left"><?php print(_T('Failed', 'msc')); ?></label>
                        <input type="checkbox" name="cbx_state[]" id="cbx_running" value="scheduled" style="top: 2px; left: 5px; position: relative; float: left" />
                        <label for="cbx_running" style="padding: 7px 10px; position: relative; float: left"><?php print(_T('In progress', 'msc')); ?></label>
                        <input type="checkbox" name="cbx_state[]" id="cbx_overtimed" value="over_timed" style="top: 2px; left: 5px; position: relative; float: left" />
                        <label for="cbx_overtimed" style="padding: 7px 10px; position: relative; float: left"><?php print(_T('Overtime', 'msc')); ?></label>
                        <input type="checkbox" name="cbx_state[]" id="cbx_stopped" value="stopped" style="top: 2px; left: 5px; position: relative; float: left" />
                        <label for="cbx_stopped" style="padding: 7px 10px; position: relative; float: left"><?php print(_T('Stopped', 'msc')); ?></label>
                        <input type="hidden" name="create_group" value="" />
                        <br/>
                        <div style="margin:2px 7px -5px 5px" align="right">
                            <input id="btnCreateGroup"  type="button" value="<?php print _T('Create a group'); ?>" class="btnPrimary">
                        </div>
                        <script type="text/javascript">
                            var $ = jQuery;
                            $(function() {
                                $('#btnCreateGroup').click(function(){
                                    var create_group_field = $(this).parents('form:first').find('input[name=create_group]');
                                    create_group_field.val('1');
                                    pushSearch<?php echo $this->divid; ?>();
                                    setTimeout(function(){
                                        create_group_field.val('');
                                    }, 1000);
                                });
                            });
                        </script>
                    </span>
                    <!-- </form> -->
                <?php } ?>

            </div>
            </div>

            <script type="text/javascript">
                var $ = jQuery;
                $(function() {
                    $('#Form input[type=checkbox]').click(pushSearch<?php echo $this->divid; ?>);
                });
                jQuery('#param').focus();
                var refreshtimer = null;
                var refreshparamtimer = null;
                var refreshdelay = <?php echo $this->refresh; ?>;

        <?php
        if (isset($this->storedfilter)) {
            ?>
                    jQuery('#<?php echo $this->formid; ?> input#param').val("<?php echo $this->storedfilter; ?>");
            <?php
        }
        ?>
                /**
                 * Clear the timers set vith setTimeout
                 */
                function clearTimers<?php echo $this->divid; ?>() {
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
                function updateSearch<?php echo $this->divid; ?>() {
                    jQuery('#<?php echo $this->divid; ?>').load('<?php echo $this->url; ?>filter=' + encodeURIComponent(jQuery('#<?php echo $this->formid; ?> input#param').val()) + '&<?php echo $this->paramname ?>=' + jQuery('#<?php echo $this->formid; ?> input#<?php echo $this->paramname ?>').val() + <?php print json_encode($this->params); ?> + '&' + jQuery('#<?php echo $this->formid; ?>').serialize(), function() {
                        jQuery('#container').unmask();
                    });
                    jQuery('#<?php echo $this->divid; ?>').mask("");
                    jQuery('#<?php echo $this->divid; ?>').width('100%');
                    jQuery('#<?php echo $this->divid; ?>').css('clear', 'right');

        <?php
        if ($this->refresh) {
            ?>
                        refreshtimer = setTimeout("updateSearch<?php echo $this->divid; ?>()", refreshdelay)
            <?php
        }
        ?>
                }

                /**
                 * Update div when clicking previous / next
                 */
                function updateSearchParam<?php echo $this->divid; ?>(filter, start, end) {
                    clearTimers<?php echo $this->divid; ?>();
                    jQuery('#<?php echo $this->divid; ?>').load('<?php echo $this->url; ?>filter=' + filter + <?php echo json_encode($this->params); ?> + '&<?php echo $this->paramname ?>=' + jQuery('#<?php echo $this->formid; ?> input#<?php echo $this->paramname ?>').val() + '&start=' + start + '&end=' + end + '&' + jQuery('#<?php echo $this->formid; ?>').serialize(), function() {
                        jQuery('#<?php echo $this->divid; ?>').unmask();
                    });
                    jQuery('#<?php echo $this->divid; ?>').mask("");
                    jQuery('#<?php echo $this->divid; ?>').width('100%');

        <?php
        if ($this->refresh) {
            ?>
                        refreshparamtimer = setTimeout("updateSearchParam<?php echo $this->divid; ?>('" + filter + "'," + start + "," + end + ")", refreshdelay);
            <?php
        }
        ?>
                }

                /**
                 * wait 500ms and update search
                 */
                function pushSearch<?php echo $this->divid; ?>() {
                    clearTimers<?php echo $this->divid; ?>();
                    refreshtimer = setTimeout("updateSearch<?php echo $this->divid; ?>()", 500);
                }

                pushSearch<?php echo $this->divid; ?>();
            </script>

        </form>
        <?php
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
        <form name="Form" id="Form" action="#" onsubmit="return false;">

            <div id="loader"><img id="loadimg" src="<?php echo $root; ?>img/common/loader.gif" alt="loader" class="loader"/></div>

            <div id="searchSpan" class="searchbox" style="float: right;">

                <span class="searchfield">
                    <?php
                    $this->commands->display();
                    $this->states->display();
                    ?>
                </span>&nbsp;

                <span class="searchfield"><input type="text" class="searchfieldreal" name="param" id="param" onkeyup="pushSearch();
                        return false;" />
                    <img src="graph/croix.gif" alt="suppression" style="position:relative; top : 3px;"
                         onclick="document.getElementById('param').value = '';
                                 pushSearch();
                                 return false;" />
                </span>
            </div>

            <script type="text/javascript">
                jQuery('#param').focus();
                var refreshtimer = null;
                var refreshparamtimer = null;
                var refreshdelay = <?php echo $this->refresh ?>;

        <?php
        if (isset($this->storedfilter)) {
            ?>
                    document.Form<?php echo $this->formid ?>.param.value = "<?php echo $this->storedfilter ?>";
            <?php
        }
        ?>
                /**
                 * Clear the timers set vith setTimeout
                 */
                function clearTimers<?php echo $this->divid; ?>() {
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
                function updateSearch<?php echo $this->divid; ?>() {
                    clearTimers<?php echo $this->divid; ?>();
                    jQuery('#<?php echo $this->divid; ?>').load('<?php echo $this->url; ?>filter=' + encodeURIComponent(document.Form.param.value) + '<?php echo $this->params ?>&<?php echo $this->paramname1 ?>=' + document.Form.<?php echo $this->paramname1 ?>.value + '&<?php echo $this->paramname2 ?>=' + document.Form.<?php echo $this->paramname2 ?>.value);

        <?php
        if ($this->refresh) {
            ?>
                        refreshtimer = setTimeout("updateSearch<?php echo $this->divid; ?>()", refreshdelay)
            <?php
        }
        ?>
                }

                /**
                 *
                 */
                function updateStates<?php echo $this->divid; ?>() {
                    var ind = document.getElementById('<?php echo $this->paramname2; ?>');
                    var val = ind.options[ind.selectedIndex].value;
                    jQuery('#<?php echo $this->paramname2; ?>').load('<?php echo urlStrRedirect('msc/logs/state_list', array('paramname2' => $this->paramname2)); ?>&<?php echo $this->paramname1 ?>=' + document.Form.<?php echo $this->paramname1 ?>.value + '&selected=' + document.Form.<?php echo $this->paramname2 ?>.value);
                    refreshtimer = setTimeout("updateSearch<?php echo $this->divid; ?>()", 500);
                }

                /**
                 * Update div when clicking previous / next
                 */
                function updateSearchParam<?php echo $this->divid; ?>(filter, start, end) {
                    clearTimers<?php echo $this->divid; ?>();
                    jQuery('#<?php echo $this->divid; ?>').load('<?php echo $this->url; ?>filter=' + filter + '<?php echo $this->params ?>&<?php echo $this->paramname1 ?>=' + document.Form.<?php echo $this->paramname1 ?>.value + '&<?php echo $this->paramname2 ?>=' + document.Form.<?php echo $this->paramname2 ?>.value + '&start=' + start + '&end=' + end);

        <?php
        if ($this->refresh) {
            ?>
                        refreshparamtimer = setTimeout("updateSearchParam<?php echo $this->divid; ?>('" + filter + "'," + start + "," + end + ")", refreshdelay);
            <?php
        }
        ?>
                }

                /**
                 * wait 500ms and update search
                 */
                function pushSearch2<?php echo $this->divid; ?>() {
                    clearTimers<?php echo $this->divid; ?>();
                    refreshtimer = setTimeout("updateSearch<?php echo $this->divid; ?>()", 750);
                }

                function pushSearch<?php echo $this->divid; ?>() {
                    clearTimers<?php echo $this->divid; ?>();
                    setTimeout("updateStates<?php echo $this->divid; ?>()", 100);
                }

                pushSearch2<?php echo $this->divid; ?>();
            </script>

        </form>
        <?php
    }

}
?>

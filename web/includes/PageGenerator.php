<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2010 Mandriva, http://www.mandriva.com
 * (c) 2021-2022 Siveo, http://siveo.net
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */
require("FormGenerator.php");
require_once("utils.inc.php");

/**
 * return an uniqId (use full for javascript auto generation
 */
function getUniqId()
{
    global $__uniqID;
    $__uniqID++;
    return $__uniqID;
}

/**
 * can echo obj and string with the same function
 * similar to "echo" in PHP5
 */
function echo_obj($obj)
{

    if (is_object($obj)) {
        echo nl2br($obj->__toString());
    } elseif (is_bool($obj)) {
        if ($obj) {
            echo '<img src="img/other/yes.svg" alt="yes" width="25" height="25" />';
        }
    } else {
        echo nl2br($obj);
    }
}

/**
 * debug print
 */
function debug($obj, $return = false)
{

    $s = '<pre style="font-family:Courier, monospace; font-weight:bold ">';
    $s .= print_r($obj, true);
    $s .= '</pre>';
    if ($return) {
        return $s;
    } else {
        print $s;
    }
}

/**
 * class for action encapsulation
 * Abstract class for the moment
 * @see EditInPlace
 */
class ActionEncapsulator
{
    public function __construct()
    {

    }

    public function __toString()
    {
        return "default action encapsulator";
    }

}

/**
 * AutoGenerate an EditInPlace text
 * based on scriptaculous javascript
 */
class EditInPlace extends ActionEncapsulator
{
    public $origText;
    public $url;
    public $param;

    public function __construct($origText, $url, $param)
    {
        $this->origText = $origText;
        $this->url = $url;
        $this->param = $param;
    }

    public function __toString()
    {

        $param = array();

        foreach ($this->param as $key => $value) {
            $param[] = "$key=$value";
        }

        $urlparam = implode("&", $param);

        if ($this->origText == '') {
            $this->origText = "n/a";
        }

        $idx = getUniqId();

        $str = '';
        $str .= "<span id=\"id$idx\" class=\"editinplace\">" . $this->origText . "</span>";


        /* $str .= '<script type="text/javascript">';
          $str .= "     new Ajax.InPlaceEditor($('id$idx'),'".$this->url."', {\n
          okButton: true, cancelLink: true, cancelText : '"._('Cancel')."',
          highlightcolor : '#FF9966',
          ajaxOptions: {method: 'get' },\n
          callback: function(form,value) {\n
          return '$urlparam&value='+value\n
          }\n
          });\n
          </script>\n"; ===> CLASS NOT USED */
        return $str;
    }

}

/**
 *  class for action in various application
 */
class ActionItem
{
    public $desc;
    public $action;
    public $classCss;
    public $paramString;
    public $module;
    public $submod;
    public $mod;
    public $path;
    public $tab;

    /**
     *  Constructor
     * @param $desc description
     * @param $action string include in the url
     * @param $classCss class for CSS like "supprimer" or other class define
     *    in the CSS global.css
     * @param $paramString add "&$param=" at the very end of the url
     */
    public function __construct($desc, $action, $classCss, $paramString, $module = null, $submod = null, $tab = null, $mod = false)
    {
        $this->desc = $desc;
        $this->action = $action;
        $this->classCss = $classCss;
        $this->paramString = $paramString;
        if ($module == null) {
            $this->module = $_GET["module"];
        } else {
            $this->module = $module;
        }
        if ($submod == null) {
            $this->submod = $_GET["submod"];
        } else {
            $this->submod = $submod;
        }
        $this->tab = $tab;
        $this->mod = $mod;
        $this->path = $this->module . "/" . $this->submod . "/" . $this->action;
        if ($this->tab != null) {
            $this->path .= "/" . $this->tab;
        }
    }

    /**
     *  display a link for the action
     *  @param add &$this->param=$param at the very end of the url
     *  display "displayWithRight" if you have correct right
     */
    public function display($param, $extraParams = array())
    {
        if (hasCorrectAcl($this->module, $this->submod, $this->action)) {
            $this->displayWithRight($param, $extraParams);
        } else {
            $this->displayWithNoRight($param, $extraParams);
        }
    }

    /**
     * display function if you have correct right on this action
     */
    public function displayWithRight($param, $extraParams = array())
    {
        /* add special param for actionItem */
        if (is_array($extraParams)) {
            $extraParams['mod'] = $this->mod;
        }
        echo "<li class=\"" . $this->classCss . "\">";
        if (is_array($extraParams) & !empty($extraParams)) {
            $urlChunk = $this->buildUrlChunk($extraParams);
        } else {
            $urlChunk = "&amp;" . $this->paramString . "=" . rawurlencode($extraParams);
        }
        echo "<a title=\"" . $this->desc . "\" href=\"" . urlStr($this->path) . $urlChunk . "\">&nbsp;</a>";
        echo "</li>";
    }

    /**
     * display function if you don't have the right for this action
     */
    public function displayWithNoRight($param, $extraParams = array())
    {
        echo "<li class=\"" . $this->classCss . "\" style=\"opacity: 0.30;\">";
        echo "<a title=\"" . $this->desc . "\" href=\"#\" onclick='return false;'>&nbsp;</a>";
        echo "</li>";
    }

    /**
     * transform $obj param in link for this action
     */
    public function encapsulate($obj, $extraParams = array())
    {
        if (hasCorrectAcl($this->module, $this->submod, $this->action)) {
            if (is_array($extraParams) & !empty($extraParams)) {
                $urlChunk = $this->buildUrlChunk($extraParams);
            } else {
                $urlChunk = "&amp;" . $this->paramString . "=" . rawurlencode($obj);
            }
            $str = "<a title=\"" . $this->desc . "\" href=\"main.php?module=" . $this->module . "&amp;submod=" . $this->submod . "&amp;action=" . $this->action . $urlChunk . "\">";
            $str .= trim($obj);
            $str .= "</a>";
            return $str;
        } else {
            $str = "<a title=\"" . $this->desc . "\" href=\"#\">";
            $str .= "$obj";
            $str .= " </a>";
            return $str;
        }
    }

    /**
     * Build an URL chunk using a array of option => value
     */
    public function buildUrlChunk($arr)
    {
        $urlChunk = "";
        foreach ($arr as $option => $value) {
            $urlChunk .= "&amp;" . $option . "=" . urlencode($value);
        }
        return $urlChunk;
    }

    /**
     * display help (not use for the moment)
     */
    public function strHelp()
    {
        $str = "";
        $str .= "<li class=\"" . $this->classCss . "\">";
        $str .= "<a title=\"" . $this->desc . "\" href=\"#\">";
        $str .= " </a>" . $this->desc . "</li>";
        return $str;
    }

}

/**
 * display action in a JavaScript popup
 *
 * @see ActionItem
 * @see showPopup (js)
 */
class ActionPopupItem extends ActionItem
{
    private $_displayType = 0;

    public function __construct($desc, $action, $classCss, $paramString, $module = null, $submod = null, $tab = null, $width = 300, $mod = false)
    {
        parent::__construct($desc, $action, $classCss, $paramString, $module, $submod, $tab, $mod);
        $this->setWidth($width);
    }

    /**
     * Set the JavaScript popup width.
     * The default width value is 300px.
     */
    public function setWidth($width)
    {
        $this->width = $width;
    }

    public function displayType($type)
    {
        $this->_displayType = $type;
    }

    public function displayWithRight($param, $extraParams = array())
    {
        /* Add special param for actionPopupItem */
        if (is_array($extraParams)) {
            $extraParams['mod'] = $this->mod;
        }
        if (is_array($extraParams) & !empty($extraParams)) {
            $urlChunk = $this->buildUrlChunk($extraParams);
        } else {
            $urlChunk = "&amp;" . $this->paramString . "=" . rawurlencode($param);
        }

        echo "<li class=\"" . $this->classCss . "\">";
        echo "<a title=\"" . $this->desc . "\" href=\"main.php?module=" . $this->module . "&amp;submod=" . $this->submod . "&amp;action=" . $this->action . $urlChunk . "\"";
        echo " onclick=\"PopupWindow(event,'main.php?module=" . $this->module . "&amp;submod=" . $this->submod . "&amp;action=" . $this->action . $urlChunk . "', " . $this->width . "); return false;\">&nbsp;</a>";
        echo "</li>";
    }

    public function encapsulate($obj, $extraParams = array())
    {
        if (is_array($extraParams) & !empty($extraParams)) {
            $urlChunk = $this->buildUrlChunk($extraParams);
        } else {
            $urlChunk = "&amp;" . $this->paramString . "=" . rawurlencode($obj);
        }
        $str = "<a title=\"" . $this->desc . "\" href=\"main.php?module=" . $this->module . "&amp;submod=" . $this->submod . "&amp;action=" . $this->action . $urlChunk . "\" ";
        $str .= "  onclick=\"showPopup(event,'main.php?module=" . $this->module . "&amp;submod=" . $this->submod . "&amp;action=" . $this->action . $urlChunk . "', " . $this->width . "); return false;\">";
        $str .= "$obj";
        $str .= " </a>";
        return $str;
    }

}

/**
 * display confirm box before redirecting to action link
 *
 * @see ActionItem
 * @see showPopup (js)
 */
class ActionConfirmItem extends ActionItem
{
    public $_displayType = 0;
    public $_confirmMessage = '';

    public function __construct($desc, $action, $classCss, $paramString, $module = null, $submod = null, $confirmMessage, $tab = null, $width = 300, $mod = false)
    {
        parent::__construct($desc, $action, $classCss, $paramString, $module, $submod, $tab, $mod);
        //$this->setWidth($width);
        $this->_confirmMessage = $confirmMessage;
    }

    public function displayWithRight($param, $extraParams = array())
    {
        /* Add special param for actionPopupItem */
        if (is_array($extraParams)) {
            $extraParams['mod'] = $this->mod;
        }
        if (is_array($extraParams) & !empty($extraParams)) {
            $urlChunk = $this->buildUrlChunk($extraParams);
        } else {
            $urlChunk = "&amp;" . $this->paramString . "=" . rawurlencode($param);
        }
        echo "<li class=\"" . $this->classCss . "\">";
        echo "<a title=\"" . $this->desc . "\" href=\"#\" ";
        echo " onclick=\"displayConfirmationPopup('" . $this->_confirmMessage . "', 'main.php?module=" . $this->module . "&amp;submod=" . $this->submod . "&amp;action=" . $this->action . $urlChunk . "')\" ";
        echo ">&nbsp;</a>";
        echo "</li>";
    }

}

class EmptyActionItem extends ActionItem
{
    public function __construct($desc = "")
    {
        $this->classCss = 'empty';
        $this->desc = $desc;
    }

    public function display($param = null, $extraParams = array())
    {
        echo "<li class=\"" . $this->classCss . "\">";
        echo "<a title=\"" . $this->desc . "\" href=\"#\" ";
        echo "onclick=\"return false;\">&nbsp;</a>";
        print "</li>";
    }
    public function setClassCss($name)
    {
        $this->classCss = $name;
    }
    public function setDescription($name)
    {
        $this->desc = $name;
    }

}

/**
 *  class who maintain array presentation of information
 */
class ListInfos extends HtmlElement
{
    public $arrInfo; /*     * < main list */
    public $extraInfo;
    public $paramInfo;
    public $name;
    public $arrAction; /*     * < list of possible action */
    public $end;
    public $start;
    public $description; /*     * < list of description (not an obligation) */
    public $col_width; /*     * < Contains the columns width */
    public $tooltip; /*     * < Contains the tooltip for column label */

    /**
     * constructor
     * @param $tab must be an array of array
     */
    public function __construct($tab, $description = "", $extranavbar = "", $width = "", $tooltip = "")
    {
        $this->arrInfo = $tab;
        $this->arrAction = array();
        $this->description[] = $description;
        $this->extranavbar = $extranavbar;
        $this->initVar();
        $this->col_width = array();
        $this->col_width[] = $width;
        $this->tooltip = array();
        $this->tooltip[] = $tooltip;
        $this->firstColumnActionLink = true;
        $this->dissociateColumnsActionLink = [];
        $this->_addInfo = array();
    }

    public function setAdditionalInfo($addinfo)
    {
        $this->_addInfo = $addinfo;
    }

    /**
     * Set the number of rows to display per ListInfos page.
     * It overrides the default value defined by $conf["global"]["maxperpage"].
     *
     * @param $value The number of rows
     */
    public function setRowsPerPage($value)
    {
        $this->end = $value;
    }

    /**
     *  add an ActionItem
     *  @param $objActionItem object ActionItem
     */
    public function addActionItem($objActionItem)
    {
        $this->arrAction[] = &$objActionItem;
    }

    /**
     * Add an array of ActionItem
     * Useful if all action items are not the same for each row of the list
     *
     */
    public function addActionItemArray($objActionItemArray)
    {
        if(is_array($objActionItemArray)) {
            $this->arrAction[] = &$objActionItemArray;
        }
    }

    /**
     *  add an array String to display
     *  @param $arrString an Array String to display
     *  @param description Table column name
     *  @param width Table column width
     *  @param tooltip Tooltip to display on the column name
     */
    public function addExtraInfo($arrString, $description = "", $width = "", $tooltip = "")
    {
        if(is_array($arrString)) {
            $this->extraInfo[] = &$arrString;
            $this->description[] = $description;
            $this->col_width[] = $width;
            $this->tooltip[] = $tooltip;
        }
    }

    /**
     *  set parameters array for main action
     *  @param $arrString an Array of string to be used as parameters for the main action
     */
    public function setParamInfo($arrString)
    {
        if(is_array($arrString)) {
            $this->paramInfo = $arrString;
        }
    }

    /**
     * Set the left padding of the table header.
     * It will be set to 32 by default
     * @param $padding an integer
     */
    public function setTableHeaderPadding($padding)
    {
        $this->first_elt_padding = $padding;
    }

    /**
     * Disable the link to the first available action in the table
     * This link is always done by default
     */
    public function disableFirstColumnActionLink()
    {
        $this->firstColumnActionLink = false;
    }

    public function dissociateColumnActionLink($ids)
    {
        foreach($ids as $id) {
            if(!in_array($id, $this->dissociateColumnsActionLink)) {
                $this->dissociateColumnsActionLink[] = intval($id);
            }
        }
    }
    /**
     *  init class' vars
     */
    public function initVar()
    {

        $this->name = "Elements";

        global $conf;

        $this->maxperpage = (isset($_REQUEST['maxperpage'])) ? $_REQUEST['maxperpage'] : $conf['global']['maxperpage'];

        if (!isset($_GET["start"])) {
            if (!isset($_POST["start"])) {
                $this->start = 0;

                if (safeCount($this->arrInfo) > 0) {
                    $this->end = $this->maxperpage - 1;
                } else {
                    $this->end = 0;
                }
            }
        } else {
            $this->start = $_GET["start"];
            $this->end = $_GET["end"];
        }
        /* Set a basic navigation bar */
        $this->setNavBar(new SimpleNavBar($this->start, $this->end, safeCount($this->arrInfo), $this->extranavbar));
    }

    /**
     *  set the name of the array (for CSS)
     */
    public function setName($name)
    {
        $this->name = $name;
    }

    /**
     *  set the cssclass of a row
     */
    public function setCssClass($name)
    {
        $this->cssClass = $name;
    }

    /**
     * set cssids for each row
     */
    public function setCssIds($a_names)
    {
        $this->cssIds = $a_names;
    }

    /**
     * set a cssclass for each row
     */
    public function setCssClasses($a_names)
    {
        $this->cssClasses = $a_names;
    }

    /**
     * set cssclass for each MainAction column
     */
    public function setMainActionClasses($classes)
    {
        $this->mainActionClasses = $classes;
    }

    /**
     * Set the ListInfos navigation bar
     */
    public function setNavBar($navbar)
    {
        $this->navbar = $navbar;
    }

    /**
     *
     * Display the widget navigation bar if $navbar is True
     *
     * @param $navbar: if $navbar is true the navigation bar is displayed
     */
    public function displayNavbar($navbar)
    {
        if ($navbar) {
            $this->navbar->display();
        }
    }

    /**
     *  draw number of page etc...
     */
    public function drawHeader($navbar = 1)
    {

        $this->displayNavbar($navbar);
        echo "<p class=\"listInfos\">";

        /*
         * Management of the numbers "start" and "end" to display depending on the maxperpage set in the selector
         * These numbers are more user-friendly and do not begin with 0
         */
        echo $this->name . " <strong>" . min($this->start + 1, safeCount($this->arrInfo)) . "</strong>\n ";
        echo _("to") . " <strong>" . min($this->end + 1, safeCount($this->arrInfo)) . "</strong>\n";

        printf(_(" - Total <b>%s </b>") . "\n", safeCount($this->arrInfo));
        /* Display page counter only when useful */
        if (safeCount($this->arrInfo) > $this->maxperpage) {
            echo "(" . _("page") . " ";
            printf("%.0f", ($this->end + 1) / $this->maxperpage);
            echo " / ";
            $pages = intval((safeCount($this->arrInfo) / $this->maxperpage));
            if ((safeCount($this->arrInfo) % $this->maxperpage > 0) && (safeCount($this->arrInfo) > $this->maxperpage)) {
                $pages++;
            } elseif ((safeCount($this->arrInfo) > 0) && ($pages < 1)) {
                $pages = 1;
            } elseif ($pages < 0) {
                $pages = 0;
            }
            printf("%.0f", $pages);
            echo ")\n";
        }
        echo "</p>";
    }

    /**
     * display main action (first action
     */
    public function drawMainAction($idx)
    {
        if (!empty($this->cssClass)) {
            echo "<td class=\"" . $this->cssClass . "\">";
        } elseif (!empty($this->mainActionClasses)) {
            echo "<td class=\"" . $this->mainActionClasses[$idx] . "\">";
        } else {
            echo "<td>";
        }
        if (is_a($this->arrAction[0], 'ActionItem')) {
            $firstAction = $this->arrAction[0];
        } elseif (is_array($this->arrAction[0])) {
            $firstAction = $this->arrAction[0][$idx];
        }
        echo $firstAction->encapsulate($this->arrInfo[$idx], $this->paramInfo[$idx]);
        if (isset($this->_addInfo[$idx])) {
            print " " . $this->_addInfo[$idx];
        }
        echo "</td>";
    }

    public function drawTable($navbar = 1)
    {
        echo "<table border=\"1\" cellspacing=\"0\" cellpadding=\"5\" class=\"listinfos\">\n";
        echo "<thead><tr>";
        $first = false;
        foreach ($this->description as $key => $desc) {
            if (isset($this->col_width[$key])) {
                $width_styl = 'width: ' . $this->col_width[$key] . ';';
            } else {
                $width_styl = '';
            }
            if (!$first) {

                if (!isset($this->first_elt_padding)) {
                    $this->first_elt_padding = 32;
                }
                echo "<td style=\"$width_styl\"><span style=\" padding-left: " . $this->first_elt_padding . "px;\">$desc</span></td>";
                $first = true;
            } else {
                /* Draw table header line */
                /* Add a tooltip to the column name if there is one set */
                if (!empty($this->tooltip[$key])) {
                    $tooltipbegin = "<a href=\"#\" class=\"tooltip\">";
                    $tooltipend = "<span>" . $this->tooltip[$key] . "</span></a>";
                } else {
                    $tooltipbegin = "";
                    $tooltipend = "";
                }
                echo "<td style=\"$width_styl\"><span style=\" \">$tooltipbegin$desc$tooltipend</span></td>";
            }
        }

        if (safeCount($this->arrAction) != 0) { //if we have actions
            if (!empty($this->col_width)) {
                $width_styl = $this->col_width[safeCount($this->col_width) - 1];
            }
            $width_styl = isset($width_styl) ? sprintf('width: %s;', $width_styl) : '';
            echo "<td style=\"text-align: center; $width_styl\"><span>Actions</span></td>";
        }

        echo "</tr></thead>";

        for ($idx = $this->start; ($idx < safeCount($this->arrInfo)) && ($idx <= $this->end); $idx++) {
            if (($this->start - $idx) % 2) {
                echo "<tr";
                if (!empty($this->cssIds[$idx])) {
                    echo " id='". $this->cssIds[$idx]."'";
                }
                if (!empty($this->cssClasses[$idx])) {
                    echo " class=\"" . $this->cssClasses[$idx] . "\"";
                }
                echo ">";
            } else {
                echo "<tr";
                if (!empty($this->cssIds[$idx])) {
                    echo " id='". $this->cssIds[$idx]."'";
                }
                echo " class=\"alternate";
                if (!empty($this->cssClasses[$idx])) {
                    echo " " . $this->cssClasses[$idx];
                }
                echo "\">";
            }


            //link to first action (if we have an action)
            if (safeCount($this->arrAction) && $this->firstColumnActionLink && !in_array($idx, $this->dissociateColumnsActionLink)) {
                $this->drawMainAction($idx);
            } else {
                if (!empty($this->cssClass)) {
                    echo "<td class=\"" . $this->cssClass . "\">";
                } elseif (!empty($this->mainActionClasses)) {
                    echo "<td class=\"" . $this->mainActionClasses[$idx] . "\">";
                } else {
                    echo "<td>";
                }
                echo $this->arrInfo[$idx];
                echo "</td>";
            }

            if ($this->extraInfo) {
                foreach ($this->extraInfo as $arrayTMP) {
                    echo "<td>";
                    if (isset($arrayTMP[$idx]) && is_subclass_of($arrayTMP[$idx], "HtmlContainer")) {
                        $arrayTMP[$idx]->display();
                    } elseif (isset($arrayTMP[$idx]) && trim($arrayTMP[$idx]) != "") {
                        echo_obj($arrayTMP[$idx]);
                    } else {
                        echo "&nbsp;";
                    }
                    echo "</td>";
                }
            }

            if (safeCount($this->arrAction) != 0) {
                echo "<td class=\"action\">";
                echo "<ul class=\"action\">";
                foreach ($this->arrAction as $objActionItem) {
                    if (is_a($objActionItem, 'ActionItem')) {
                        $objActionItem->display($this->arrInfo[$idx], $this->paramInfo[$idx]);
                    } elseif (is_array($objActionItem)) {
                        $obj = $objActionItem[$idx];
                        $obj->display($this->arrInfo[$idx], $this->paramInfo[$idx]);
                    }
                }
                echo "</ul>";
                echo "</td>";
            }
            echo "</tr>\n";
        }


        echo "</table>\n";

        $this->displayNavbar($navbar);

        if (false) {
            /* Code disabled because not used and make javavascript errors */
            print '<script type="text/javascript"><!--';
            print "jQuery('#help').html('');\n";
            print '$(\'help\').innerHTML+=\'<ul>\'' . "\n";
            print '$(\'help\').innerHTML+=\'<li><h3>Aide contextuelle</h3></li>\'' . "\n";
            foreach ($this->arrAction as $objActionItem) {
                $content = $objActionItem->strHelp();
                print '$(\'help\').innerHTML+=\'' . $content . '\';' . "\n";
            }
            print '$(\'help\').innerHTML+=\'</ul>\'' . "\n";
            print '--></script>';
        }
    }

    public function display($navbar = 1, $header = 1)
    {
        if (!isset($this->paramInfo)) {
            $this->paramInfo = $this->arrInfo;
        }
        if ($header == 1) {
            $this->drawHeader($navbar);
        }
        $this->drawTable($navbar);
    }

}

/**
 * A modified version of Listinfos
 */
class OptimizedListInfos extends ListInfos
{
    /**
     * Allow to set another item count
     */
    public function setItemCount($count)
    {
        $this->itemCount = $count;
    }

    public function getItemCount()
    {
        return $this->itemCount;
    }

    /**
     *  init class' vars
     */
    public function initVar()
    {
        $this->name = "Elements";
        global $conf;
        if (!isset($_GET["start"])) {
            if (!isset($_POST["start"])) {
                $this->start = 0;
                if (safeCount($this->arrInfo) > 0) {
                    $this->end = (isset($_REQUEST['maxperpage'])) ? ($_REQUEST['maxperpage'] - 1) : ($conf["global"]["maxperpage"] - 1);
                } else {
                    $this->end = 0;
                }
            }
        } else {
            $this->start = $_GET["start"];
            $this->end = $_GET["end"];
        }
        $this->maxperpage = (isset($_REQUEST['maxperpage'])) ? $_REQUEST['maxperpage'] : $conf["global"]["maxperpage"];
        $this->setItemCount(safeCount($this->arrInfo));
        $this->startreal = $this->start;
        $this->endreal = $this->end;
    }

    /**
     *  draw number of page etc...
     */
    public function drawHeader($navbar = 1)
    {
        $count = $this->getItemCount();
        $this->displayNavbar($navbar);
        echo "<p class=\"listInfos\">";

        /*
         * Management of the numbers "start" and "end" to display depending on the maxperpage set in the selector
         * These numbers are more user-friendly and do not begin with 0
         */
        echo $this->name . " <strong>" . min($this->startreal + 1, $count) . "</strong>\n ";
        echo _("to") . " <strong>" . min($this->endreal + 1, $count) . "</strong>\n";

        printf(_(" - Total <b>%s </b>") . "\n", $count);
        /* Display page counter only when useful */
        if ($count > $this->maxperpage) {
            echo "(" . _("page") . " ";
            printf("%.0f", ($this->endreal + 1) / $this->maxperpage);
            echo " / ";
            $pages = intval(($count / $this->maxperpage));
            if (($count % $this->maxperpage > 0) && ($count > $this->maxperpage)) {
                $pages++;
            } elseif (($count > 0) && ($pages < 1)) {
                $pages = 1;
            } elseif ($pages < 0) {
                $pages = 0;
            }
            printf("%.0f", $pages);
            echo ")\n";
        }
        echo "</p>";
    }

}

/**
 * specific class for UserDisplay
 */
class UserInfos extends OptimizedListInfos
{
    public $css = array(); //css for first column

    public function drawMainAction($idx)
    {
        echo "<td class=\"" . $this->css[$idx] . "\">";
        echo $this->arrAction[0]->encapsulate($this->arrInfo[$idx], $this->paramInfo[$idx]);
        echo "</td>";
    }

}

/**
 *
 *  Display a previous/next navigation bar for ListInfos widget
 *
 */
class SimpleNavBar extends HtmlElement
{
    /**
     * @param $curstart: the first item index to display
     * @param $curent: the last item index
     * @param $itemcount: total number of item
     * @param $filter: the current list filter
     * @param $max: max quantity of elements in a page
     * @param $paginator: boolean which enable the selector of the number of results in a page
     */
    public function __construct($curstart, $curend, $itemcount, $extra = "", $max = "", $paginator = false)
    {
        global $conf;
        if (isset($max) && $max != "") {
            $this->max = $max;
        } else {
            $this->max = $conf["global"]["maxperpage"];
        }
        $this->curstart = $curstart;
        $this->curend = $curend;
        $this->itemcount = $itemcount;
        $this->extra = $extra;
        $this->paginator = $paginator;
        # number of pages
        $this->nbpages = ceil($this->itemcount / $this->max);
        # number of current page
        $this->curpage = floor(($this->curend + 1) / $this->max);
    }

    public function display($arrParam = array())
    {
        echo '<form method="post">';
        echo "<ul class=\"navList\">\n";

        if ($this->curstart != 0 || ($this->curstart - $this->max > 0)) {
            $start = $this->curstart - $this->max;
            $end = $this->curstart - 1;
            echo "<li class=\"previousList\"><a href=\"" . $_SERVER["SCRIPT_NAME"];
            /* FIXME: maybe we can get rid of $_GET["filter"] ? */
            printf("?module=%s&amp;submod=%s&amp;action=%s&amp;start=%d&amp;end=%d&amp;filter=%s%s", $_GET["module"], $_GET["submod"], $_GET["action"], $start, $end, $_GET["filter"], $this->extra);
            echo "\">" . _("Previous") . "</a></li>\n";
        }

        if ($this->paginator) {
            // Display the maxperpage selector
            $this->displaySelectMax();
        }

        if (($this->curend + 1) < $this->itemcount) {
            $start = $this->curend + 1;
            $end = $this->curend + $this->max;
            $filter = isset($_GET["filter"]) ? $_GET["filter"] : "";
            echo "<li class=\"nextList\"><a href=\"" . $_SERVER["SCRIPT_NAME"];
            printf("?module=%s&amp;submod=%s&amp;action=%s&amp;start=%d&amp;end=%d&amp;filter=%s%s", $_GET["module"], $_GET["submod"], $_GET["action"], $start, $end, $filter, $this->extra);
            echo "\">" . _("Next") . "</a></li>\n";
        }

        if ($this->paginator) {
            // Display a border at the left of the "Next" link
            $this->displayNextListBorder();
        }

        echo "</ul></form>\n";
    }

    /*
     * This function displays a selector to choose the maxperpage value
     * dynamically.
     * This is useful with AjaxNavBar
     * @param $jsfunc: optional javascript function which updates ListInfos
     */

    public function displaySelectMax($jsfunc = null)
    {
        global $conf;
        echo '<span class="pagination">' . _('Pagination') . ': ';
        if (isset($jsfunc)) {
            $start = $this->curstart;

            echo "<select id=\"maxperpage\" name=\"maxperpage\" onChange=\"updateMaxPerPage(this); return false;\">";
        } else {
            echo "<select id=\"maxperpage\" name=\"maxperpage\">";
        }
        /* Display the selector and each option of the array set in the config
          file */
        foreach ($conf["global"]["pagination"] as $quantity) {
            $selected = '';
            if ($_REQUEST['maxperpage'] == $quantity) {
                /* Set by default if already selected before */
                $selected = ' selected="selected"';
            }
            echo "<option value=\"$quantity\"$selected>$quantity</option>";
        }
        echo "</select></span>";

        /*
         * Print the script which will launch an update of the ListInfos when
         * selectMax value changes.
         * It also synchronizes the value of the two selectors of the widget.
         * Then it calls the javascript function which do an AJAX update of
         * the ListInfos.
         */
        ?>
        <script type="text/javascript">
            updateMaxPerPage = function(elem) {
                // Get the selector element (the first of the page)
                var maxperpageElement = document.getElementById('maxperpage');
                if (jQuery('#maxperpage').length)
                {
                    jQuery('#maxperpage').val(jQuery(elem).val());
                    var maxperpageValue = jQuery('#maxperpage').val();
                    // Evaluate the end depending on the maxperpage value selected
                    var end = parseInt(maxperpageValue) + parseInt(<?php echo $start ?>) - 1;
                    // Call the function to update the ListInfos
        <?php echo $jsfunc ?>('<?php echo $this->filter ?>', '<?php echo $start ?>', end);
                }

                return false;
            }
        </script>
        <?php
    }

    /**
     * This function just print a script which add a border at the left of the "Next" link
     */
    public function displayNextListBorder()
    {
        ?>
        <script type="text/javascript">
            jQuery('.nextListInactive').css('borderLeft', 'solid 1px #CCC');
            jQuery('.nextList').css('borderLeft', 'solid 1px #CCC');
        </script>
        <?php
    }

    public function displayGotoPageField()
    {
        echo '
        <script type="text/javascript">
            gotoPage = function(input) {
                page = input.value;
                if (page <= ' . $this->nbpages . ') {
                    end = (' . $this->max . ' * page);
                    start = end - ' . $this->max . ';
                    end -= 1;
                    cur =  (' . $this->curend . ' + 1) / 10;
                    ' . $this->jsfunc . '("' . $this->filter . '", start, end, document.getElementById("maxperpage"));
                }
            }
        </script>';
        echo '<span class="pagination">' . _("Go to page") . ': <input type="text" size="2" onchange="gotoPage(this)" /></span>';
    }

    public function displayPagesNumbers()
    {
        # pages links
        # show all pages
        if ($this->nbpages <= 10) {
            if ($this->nbpages > 1) {
                echo '<span class="pagination">';
                for ($i = 1; $i <= $this->nbpages; $i++) {
                    echo $this->makePageLink($i);
                }
                echo '</span>';
            }
        }
        # show start/end pages and current page
        else {
            echo '<span class="pagination">';
            for ($i = 1; $i <= 3; $i++) {
                echo $this->makePageLink($i);
            }
            if ($this->curpage > 2 and $this->curpage < 5) {
                for ($i = $this->curpage; $i <= $this->curpage + 2; $i++) {
                    if ($i > 3) {
                        echo $this->makePageLink($i);
                    }
                }
            } elseif ($this->curpage > 4 and $this->curpage < $this->nbpages - 3) {
                echo '.. ';
                for ($i = $this->curpage - 1; $i <= $this->curpage + 1; $i++) {
                    echo $this->makePageLink($i);
                }
            }
            echo '.. ';
            if ($this->curpage <= $this->nbpages - 2 and $this->curpage >= $this->nbpages - 3) {
                for ($i = $this->nbpages - 4; $i <= $this->nbpages - 3; $i++) {
                    echo $this->makePageLink($i);
                }
            }
            for ($i = $this->nbpages - 2; $i <= $this->nbpages; $i++) {
                echo $this->makePageLink($i);
            }
            echo '</span>';
        }
    }

    public function makePageLink($page)
    {
        $end = ($this->max * $page);
        $start = $end - $this->max;
        $end -= 1;
        if ($page == $this->curpage) {
            return '<span>' . $page . '</span> ';
        } else {
            return '<a href="#" onclick="' . $this->jsfunc . '(\'' . $this->filter . '\',\'' . $start . '\',\'' . $end . '\', document.getElementById(\'maxperpage\')); return false;">' . $page . '</a> ';
        }
    }

}

/**
 * Class which creates a SimpleNavBar with the paginator always enabled by
 * default
 */
class SimplePaginator extends SimpleNavBar
{
    /**
     * Just call the constructor of SimpleNavBar with "true" value for the
     * $paginator attribute
     *
     * @param $curstart: the first item index to display
     * @param $curent: the last item index
     * @param $itemcount: total number of item
     * @param $filter: the current list filter
     * @param $max: max quantity of elements in a page
     */
    public function __construct($curstart, $curend, $itemcount, $extra = "", $max = "")
    {
        parent::__construct($curstart, $curend, $itemcount, $extra, $max, true);
    }

}

/**
 *  Display a previous/next navigation bar for ListInfos widget
 *  The AjaxNavBar is useful when an Ajax Filter is set for a ListInfos widget
 */
class AjaxNavBar extends SimpleNavBar
{
    /**
     *
     * The AjaxNavBar start/end item are get from $_GET["start"] and
     * $_GET["end"]
     *
     * @param $itemcount: total number of item
     * @param $filter: the current list filter
     * @param $extra: extra URL parameter to pass the next/list button
     * @param $jsfunc: the name of the javascript function that applies the AJAX filter for the ListInfos widget
     * @param $max: the max number of elements to display in a page
     */
    public function __construct($itemcount, $filter, $jsfunc = "updateSearchParam", $max = "", $paginator = false)
    {
        global $conf;

        if (isset($_GET["start"])) {
            $curstart = $_GET["start"];
            $curend = $_GET["end"];
        } else {
            $curstart = 0;
            if ($itemcount > 0) {
                if ($max != "") {
                    $curend = $max - 1;
                } else {
                    $curend = $conf["global"]["maxperpage"] - 1;
                }
            } else {
                $curend = 0;
            }
        }
        parent::__construct($curstart, $curend, $itemcount, null, $max, $paginator);
        $this->filter = $filter;
        $this->jsfunc = $jsfunc;
        if (isset($_GET['divID'])) {
            $this->jsfunc = $this->jsfunc . $_GET['divID'];
        }
    }

    public function display($arrParam = array())
    {
        echo '<form method="post">';
        echo "<ul class=\"navList\">\n";

        if ($this->paginator) {
            // Display the maxperpage selector
            $this->displaySelectMax($this->jsfunc);
        }

        // show goto page field
        if ($this->nbpages > 20) {
            $this->displayGotoPageField();
        }

        # previous link
        if ($this->curstart != 0 || ($this->curstart - $this->max > 0)) {
            $start = $this->curstart - $this->max;
            $end = $this->curstart - 1;
            echo "<li class=\"previousList\"><a href=\"#\" onClick=\"" . $this->jsfunc . "('" . $this->filter . "','$start','$end', document.getElementById('maxperpage')); return false;\">" . _("Previous") . "</a></li>\n";
        }

        // display pages numbers
        $this->displayPagesNumbers();

        # next link
        if (($this->curend + 1) < $this->itemcount) {
            $start = $this->curend + 1;
            $end = $this->curend + $this->max;
            echo "<li class=\"nextList\"><a href=\"#\" onClick=\"" . $this->jsfunc . "('" . $this->filter . "','$start','$end', document.getElementById('maxperpage')); return false;\">" . _("Next") . "</a></li>\n";
        }

        // Display a border at the left of the "Next" link
        if ($this->nbpages > 1) {
            $this->displayNextListBorder();
        }

        echo "</ul>\n";
    }

}

/**
 * Class which creates an AjaxNavBar with the paginator always enabled by
 * default
 */
class AjaxPaginator extends AjaxNavBar
{
    /**
     * Just call the constructor of AjaxNavBar with "true" value for the $paginator attribute
     *
     * @param $itemcount: total number of item
     * @param $filter: the current list filter
     * @param $jsfunc: the name of the javascript function that applies the AJAX filter for the ListInfos widget
     * @param $max: the max number of elements to display in a page
     */
    public function __construct($itemcount, $filter, $jsfunc = "updateSearchParam", $max = "")
    {
        parent::__construct($itemcount, $filter, $jsfunc, $max, true);
        parent::__construct($itemcount, $filter, $jsfunc, $max, true);
    }

}

/**
 *
 * Create an AjaxFilter Form that updates a div according to an url output
 *
 */
class AjaxFilter extends HtmlElement
{
    /**
     * @param $url: URL called by the javascript updated. The URL gets the filter in $_GET["filter"]
     * @param $divid: div ID which is updated by the URL output
     * @param $formid: change the form id (usefull for multiple Ajaxfilter in one page)
     */
    public function __construct($url, $divid = "container", $params = array(), $formid = "")
    {
        if (strpos($url, "?") === false) {
            /* Add extra ? needed to build the URL */
            $this->url = $url . "?";
        } else {
            /* Add extra & needed to build the URL */
            $this->url = $url . "&";
        }
        $this->divid = $divid;
        $this->formid = $formid;
        $this->refresh = 0;
        $this->params = '';
        foreach ($params as $k => $v) {
            $this->params .= "&" . $k . "=" . $v;
        }

        // get the current module pages
        if (isset($_GET["module"])) {
            $__module = $_GET["module"];
        } else {
            $__module = "default";
        }
        if (isset($_GET["submod"])) {
            $__submod = $_GET["submod"];
        } else {
            $__submod = "default";
        }
        if (isset($_GET["action"])) {
            $__action = $_GET["action"];
        } else {
            $__action = "default";
        }
        if (isset($_GET['tab'])) {
            $__tab = $_GET['tab'];
        } else {
            $__tab = "default";
        }
        $extra = "";
        foreach ($_GET as $key => $value) {
            if (!in_array($key, array('module', 'submod', 'tab', 'action', 'filter', 'start', 'end', 'maxperpage'))) {
                $extra .= $key . "_". $value;
            }
        }
        // then get our filter info
        if (isset($_SESSION[$__module . "_" . $__submod . "_" . $__action . "_" . $__tab . "_filter_" . $extra])) {
            $this->storedfilter = $_SESSION[$__module . "_" . $__submod . "_" . $__action . "_" . $__tab . "_filter_" . $extra];
        }
        if (isset($_SESSION[$__module . "_" . $__submod . "_" . $__action . "_" . $__tab . "_maxperpage_" . $extra])) {
            $this->storedmax = $_SESSION[$__module . "_" . $__submod . "_" . $__action . "_" . $__tab . "_maxperpage_" . $extra];
        }
        if (isset($_SESSION[$__module . "_" . $__submod . "_" . $__action . "_" . $__tab . "_start_" . $extra])) {
            $this->storedstart = $_SESSION[$__module . "_" . $__submod . "_" . $__action . "_" . $__tab . "_start_" . $extra];
        }
        if (isset($_SESSION[$__module . "_" . $__submod . "_" . $__action . "_" . $__tab . "_end_" . $extra])) {
            $this->storedend = $_SESSION[$__module . "_" . $__submod . "_" . $__action . "_" . $__tab . "_end_" . $extra];
        }
    }

    /**
     * Allow the list to refresh
     * @param $refresh: time in ms
     */
    public function setRefresh($refresh)
    {
        $this->refresh = $refresh;
    }

    public function display($arrParam = array())
    {
        global $conf;
        $root = $conf["global"]["root"];
        $maxperpage = $conf["global"]["maxperpage"];
        ?>
        <form name="Form<?php echo $this->formid ?>" id="Form<?php echo $this->formid ?>" action="#" onsubmit="return false;" style="margin-bottom:20px;margin-top:20px;">

            <div id="loader<?php echo $this->formid ?>">
                <img id="loadimg" src="<?php echo $root; ?>img/common/loader.gif" alt="loader" class="loader"/>
            </div>
            <div id="searchSpan<?php echo $this->formid ?>" class="searchbox" style="float: right;">
            <div id="searchBest">
                <input type="text" class="searchfieldreal" name="param" id="param<?php echo $this->formid ?>"/>
                <img class="searchfield" src="graph/croix.gif" alt="suppression" style="position:relative;"
                     onclick="document.getElementById('param<?php echo $this->formid ?>').value = '';
                             pushSearch<?php echo $this->formid ?>();
                             return false;" />
                 <button style="margin-left:20px;" onclick="pushSearch<?php echo $this->formid ?>();
                         return false;"><?php echo _T("Search", "glpi");?></button>
            </div>
            </div>

            <script type="text/javascript">
        <?php
        if (!$this->formid) {
            ?>
                    jQuery('#param<?php echo $this->formid ?>').focus();
            <?php
        }
        if (isset($this->storedfilter)) {
            ?>
                    document.Form<?php echo $this->formid ?>.param.value = "<?php echo $this->storedfilter ?>";
            <?php
        }
        ?>
                var refreshtimer<?php echo $this->formid ?> = null;
                var refreshparamtimer<?php echo $this->formid ?> = null;
                var refreshdelay<?php echo $this->formid ?> = <?php echo $this->refresh ?>;
                var maxperpage = <?php echo $maxperpage ?>;
        <?php
        if (isset($this->storedmax)) {
            ?>
                    maxperpage = <?php echo $this->storedmax ?>;
            <?php
        }
        ?>
                if (jQuery('#maxperpage').length)
                    maxperpage = jQuery('#maxperpage').val();

                /**
                 * Clear the timers set vith setTimeout
                 */
                clearTimers<?php echo $this->formid ?> = function() {
                    if (refreshtimer<?php echo $this->formid ?> != null) {
                        clearTimeout(refreshtimer<?php echo $this->formid ?>);
                    }
                    if (refreshparamtimer<?php echo $this->formid ?> != null) {
                        clearTimeout(refreshparamtimer<?php echo $this->formid ?>);
                    }
                }

                /**
                 * Update div
                 */
        <?php
        $url = $this->url . "filter='+encodeURIComponent(document.Form" . $this->formid . ".param.value)+'&maxperpage='+maxperpage+'" . $this->params;
        if (isset($this->storedstart) && isset($this->storedend)) {
            $url .= "&start=" . $this->storedstart . "&end=" . $this->storedend;
        }
        ?>

                updateSearch<?php echo $this->formid ?> = function() {
                    jQuery.ajax({
                        'url': '<?php echo $url ?>',
                        type: 'get',
                        success: function(data) {
                            jQuery("#<?php echo $this->divid; ?>").html(data);
                        }
                    });

        <?php
        if ($this->refresh) {
            ?>
                        refreshtimer<?php echo $this->formid ?> = setTimeout("updateSearch<?php echo $this->formid ?>()", refreshdelay<?php echo $this->formid ?>)
            <?php
        }
        ?>
                }

                /**
                 * Update div when clicking previous / next
                 */
                updateSearchParam<?php echo $this->formid ?> = function(filter, start, end, max) {
                    clearTimers<?php echo $this->formid ?>();
                    if (jQuery('#maxperpage').length)
                        maxperpage = jQuery('#maxperpage').val();

                    jQuery.ajax({
                        'url': '<?php echo $this->url; ?>filter=' + filter + '&start=' + start + '&end=' + end + '&maxperpage=' + maxperpage + '<?php echo $this->params ?>',
                        type: 'get',
                        success: function(data) {
                            jQuery("#<?php echo $this->divid; ?>").html(data);
                        }
                    });
        <?php
        if ($this->refresh) {
            ?>
                        refreshparamtimer<?php echo $this->formid ?> = setTimeout("updateSearchParam<?php echo $this->formid ?>('" + filter + "'," + start + "," + end + "," + maxperpage + ")", refreshdelay<?php echo $this->formid ?>);
            <?php
        }
        ?>
                }

                /**
                 * wait 500ms and update search
                 */
                pushSearch<?php echo $this->formid ?> = function() {
                    clearTimers<?php echo $this->formid ?>();
                    refreshtimer<?php echo $this->formid ?> = setTimeout("updateSearch<?php echo $this->formid ?>()", 500);
                }

                pushSearch<?php echo $this->formid ?>();

            </script>

        </form>
        <?php
    }

    public function displayDivToUpdate()
    {
        print '<div id="' . $this->divid . '"></div>' . "\n";
    }

}

class multifieldTpl extends AbstractTpl
{
    public $fields;

    public function __construct($fields)
    {
        $this->fields = $fields;
    }

    public function display($arrParam = array())
    {
        if (!isset($this->fields)) {
            return;
        }
        $separator = isset($arrParam['separator']) ? $arrParam['separator'] : ' &nbsp;&nbsp; ';

        for ($i = 0 ; $i < safeCount($this->fields) ; $i++) {
            $params = array();
            foreach($arrParam as $key => $value) {
                if(isset($value[$i])) {
                    $params[$key] = $value[$i];
                }
            }
            $this->fields[$i]->display($params);
            echo $separator;
        }
    }
}

class textTpl extends AbstractTpl
{
    public function __construct($text)
    {
        $this->text = $text;
    }

    public function display($arrParam = array())
    {
        echo $this->text;
    }
}

class NoLocationTpl extends AbstractTpl
{
    public function __construct($name)
    {
        $this->name = $name;
        $this->size = '13';
    }

    public function display($arrParam = array())
    {
        print '<span class="error">' . _("No item available") . '</span>';
        print '<input name="' . $this->name . '" id="' . $this->name . '" type="HIDDEN" size="' . $this->size . '" value="" class="searchfieldreal" />';
    }

    public function setSelected($elemnt)
    {

    }

}

class SingleLocationTpl extends AbstractTpl
{
    public function __construct($name, $label)
    {
        $this->name = $name;
        $this->label = $label;
        $this->value = null;
    }

    public function setElementsVal($value)
    {
        $this->value = array_values($value);
        $this->value = $this->value[0];
    }

    public function setSelected($elemnt)
    {

    }

    public function display($arrParam = array())
    {
        print $this->label;
        print '<input name="' . $this->name . '" id="' . $this->name . '" type="HIDDEN" value="' . $this->value . '" class="searchfieldreal" />';
    }

}

class AjaxFilterLocation extends AjaxFilter
{
    public function __construct($url, $divid = "container", $paramname = 'location', $params = array())
    {
        parent::__construct($url, $divid, $params);
        $this->location = new SelectItem($paramname, 'pushSearch', 'searchfieldreal noborder');
        $this->paramname = $paramname;
        $this->checkbox = array();
        $this->onchange = "pushSearch(); return false;";
    }
    public function addCheckbox($checkbox)
    {
        $checkbox->onchange = $this->onchange;
        $this->checkbox[] = $checkbox;
    }
    public function setElements($elt)
    {
        if (safeCount($elt) == 0) {
            $this->location = new NoLocationTpl($this->paramname);
        } elseif (safeCount($elt) == 1) {
            $loc = array_values($elt);
            $this->location = new SingleLocationTpl($this->paramname, $loc[0]);
        } else {
            $this->location->setElements($elt);
        }
    }

    public function setElementsVal($elt)
    {
        if (safeCount($elt) >= 1) {
            $this->location->setElementsVal($elt);
        }
    }

    public function setSelected($elemnt)
    {
        $this->location->setSelected($elemnt);
    }

    public function display($arrParam = array())
    {
        global $conf;
        $root = $conf["global"]["root"];
        ?>
        <form name="Form" id="Form" action="#" onsubmit="return false;">
            <div id="loader"><img id="loadimg" src="<?php echo $root; ?>img/common/loader.gif" alt="loader" class="loader"/></div>
            <div id="searchSpan" class="searchbox" style="float: right;">
            <div id="searchBest">
                <?php foreach ($this->checkbox as $checkbox) {
                    $checkbox->display();
                }
        ?>
                <span class="searchfield">
                    <?php
        $this->location->display();
        ?>
                </span>
                <input type="text" class="searchfieldreal" name="param" id="param" onkeyup="pushSearch();
                        return false;" />
                    <img class="searchfield" src="graph/croix.gif" alt="suppression" style="position:relative;"
                         onclick="document.getElementById('param').value = '';
                                 pushSearch();
                                 return false;" />
            </div>
            </div>

            <script type="text/javascript">
                jQuery('#param').focus();
                if(!(navigator.userAgent.toLowerCase().indexOf('chrome') > -1)) {
                    jQuery("#searchBest").width(jQuery("#searchBest").width()+20);
                }

        <?php
        if (isset($this->storedfilter)) {
            ?>
                    document.Form.param.value = "<?php echo $this->storedfilter ?>";
            <?php
        }
        ?>
                var maxperpage = <?php echo $conf["global"]["maxperpage"] ?>;
                if (jQuery('#maxperpage').length)
                    maxperpage = jQuery('#maxperpage').val();

                /**
                 * update div with user
                 */
                function updateSearch() {
                    /*add checkbox param*/
                    var strCheckbox ="";
                    jQuery(".checkboxsearch").each(function() {
                        if (jQuery(this).is(":checked")) {
                            strCheckbox+='&'+jQuery(this).attr('id')+"=true";
                        }
                    });
                    launch--;
                    if (launch == 0) {
                        jQuery.ajax({
                            'url': '<?php echo $this->url; ?>filter=' + encodeURIComponent(document.Form.param.value) + '<?php echo $this->params ?>&<?php echo $this->paramname ?>=' + document.Form.<?php echo $this->paramname ?>.value + '&maxperpage=' + maxperpage +strCheckbox,
                            type: 'get',
                            success: function(data) {
                                jQuery("#<?php echo $this->divid; ?>").html(data);
                            }
                        });
                    }
                }

                /**
                 * provide navigation in ajax for user
                 */

                function updateSearchParam(filt, start, end) {
                    /*add checkbox param*/
                    var strCheckbox ="";
                    jQuery(".checkboxsearch").each(function() {
                        if (jQuery(this).is(":checked")) {
                            strCheckbox+='&'+jQuery(this).attr('id')+"=true";
                        }
                    });
                    var reg = new RegExp("##", "g");
                    var tableau = filt.split(reg);
                    var location = "";
                    var filter = "";
                    var reg1 = new RegExp(tableau[0] + "##", "g");
                    if (filt.match(reg1)) {
                        if (tableau[0] != undefined) {
                            filter = tableau[0];
                        }
                        if (tableau[1] != undefined) {
                            location = tableau[1];
                        }
                    } else if (tableau.length == 1) {
                        if (tableau[0] != undefined) {
                            location = tableau[0];
                        }
                    }
                    if (jQuery('#maxperpage').length)
                        maxperpage = jQuery('#maxperpage').val();
                    if (!location)
                        location = document.Form.<?php echo $this->paramname ?>.value;
                    if (!filter)
                        filter = document.Form.param.value;

                    jQuery.ajax({
                        'url': '<?php echo $this->url; ?>filter=' + encodeURIComponent(filter) + '<?php echo $this->params ?>&<?php echo $this->paramname ?>=' + location + '&start=' + start + '&end=' + end + '&maxperpage=' + maxperpage +strCheckbox,
                        type: 'get',
                        success: function(data) {
                            jQuery("#<?php echo $this->divid; ?>").html(data);
                        }
                    });

                }

                /**
                 * wait 500ms and update search
                 */

                function pushSearch() {
                    launch++;
                    setTimeout("updateSearch()", 500);
                }

                pushSearch();
            </script>

        </form>
        <?php
    }

}

class AjaxLocation extends AjaxFilterLocation
{
    public function __construct($url, $divid = "container", $paramname = 'location', $params = array())
    {
        parent::__construct($url, $divid, $paramname, $params);
        $this->location = new SelectItem($paramname, 'pushSearchLocation', 'searchfieldreal noborder');
        $this->onchange = "pushSearchLocation(); return false;";
    }
    public function display($arrParam = array())
    {
        global $conf;
        $root = $conf["global"]["root"];
        ?>
        <form name="FormLocation" id="FormLocation" action="#" onsubmit="return false;">
            <div id="Location">
                <span id="searchSpan" class="searchbox">
                    <?php foreach ($this->checkbox as $checkbox) {
                        $checkbox->display();
                    }
        ?>
                    <span class="locationtext">&nbsp;<?php echo _("Select entity") ?>:&nbsp;</span>
                    <span class="locationfield">
                        <?php
            $this->location->display();
        ?>
                    </span>
                </span>
                <img id="loadimg" src="<?php echo $root; ?>img/common/loader.gif" alt="loader" />
            </div>


            <script type="text/javascript">
                /**
                 * update div with user
                 */
                function updateSearchLocation() {
                    /*add checkbox param*/
                    var strCheckbox ="";
                    jQuery(".checkboxsearch").each(function() {
                        if (jQuery(this).is(":checked")) {
                            strCheckbox+='&'+jQuery(this).attr('id')+"=true";
                        }
                    });
                    launch--;
                    if (launch == 0) {
                        jQuery.ajax({
                            'url': '<?php echo $this->url; ?><?php echo $this->params ?>&<?php echo $this->paramname ?>=' + document.FormLocation.<?php echo $this->paramname ?>.value + strCheckbox,
                            type: 'get',
                            success: function(data) {
                                jQuery("#<?php echo $this->divid; ?>").html(data);
                            }
                        });

                    }
                }
                /**
                 * wait 500ms and update search
                 */

                function pushSearchLocation() {
                    launch++;
                    setTimeout("updateSearchLocation()", 500);
                }
                pushSearchLocation();
            </script>

        </form>
        <?php
    }

}
class Checkbox
{
    public function __construct($paramname, $description)
    {
        $this->paramname = $paramname;
        $this->description = $description;
        $this->onchange = "";
    }
    public function display($arrParam = array())
    {
        global $conf;
        $root = $conf["global"]["root"];
        ?>
        <input checked style="top: 2px; left: 5px; position: relative; float: left"
        type="checkbox"
        class="checkboxsearch"
        name="<?php echo $this->paramname ?>"
        id="<?php echo  $this->paramname ?>" onchange=" <?php echo $this->onchange ?> "/>
        <span style="padding: 7px 15px; position: relative; float: left"><?php echo $this->description ?></span>
        <?php
    }
}

/**
 *  side menu items class
 *     this class is required by SideMenu class
 *     each SideMenuItem is all necessary information to
 *     create a link.
 *
 *     ex: create action "bar" in module "foo" with submodule "subfoo"
 *     new SideMenuItem("foobar example","foo","subfoo","bar");
 */
class SideMenuItem
{
    public $text;
    public $module;
    public $submod;
    public $action;
    public $activebg;
    public $inactivebg;

    /**
     *  main constructor
     * @param $text text for the link
     * @param $module module for link
     * @param $submod sub module for link
     * @param $action action param for link /!\ use for class id too
     * @param $activebg background image to use when menu is currently activated
     * @param $inactivebg background image to use when menu is currently inactivated
     */
    public function __construct($text, $module, $submod, $action, $activebg = "", $inactivebg = "")
    {
        $this->text = $text;
        $this->module = $module;
        $this->submod = $submod;
        $this->action = $action;
        $this->cssId = $action;
        $this->activebg = $activebg;
        $this->inactivebg = $inactivebg;
    }

    /**
     * @return a formated link like: main.php?module=base&submod=users&action=add
     *
     */
    public function getLink()
    {
        return 'main.php?module=' . $this->module . '&amp;submod=' . $this->submod . '&amp;action=' . $this->action;
    }

    /**
     *  display the SideMenuItem on the screen
     */
    public function display()
    {
        if (hasCorrectAcl($this->module, $this->submod, $this->action)) {
            echo '<li id="' . $this->cssId . '">';
            echo '<a href="' . $this->getLink() . '">' . $this->text . '</a></li>';
        }
    }

    /**
     * Allows to set another CSS id then the default one which is the action
     * string
     *
     * @param id: the CSS id to use
     */
    public function setCssId($id)
    {
        $this->cssId = $id;
    }

    /**
     * Return the menu item CSS
     *
     * @param active: this menu item is active
     */
    public function getCss($active = false)
    {
        $bgi_active = $bgi_inactive = "";
        if ($this->activebg != "" && $this->inactivebg != "") {
            $bgi_active = "background-image: url(" . $this->activebg . ");";
            $bgi_inactive = "background-image: url(" . $this->inactivebg . ");";
        }

        if ($active) {
            return "#sidebar ul.$this->submod li#$this->cssId a {
                        background-color: #8CB63C;
                        color: #fff;
                        $bgi_active
            }";
        } elseif ($bgi_inactive) {
            return "#sidebar ul.$this->submod li#$this->cssId a {
                        $bgi_inactive
                    }
                    #sidebar ul.$this->submod li#$this->cssId a:hover {
                        $bgi_active
                    }";
        }

        return;
    }

}

class SideMenuItemNoAclCheck extends SideMenuItem
{
    /**
     *  display the SideMenuItem on the screen
     */
    public function display()
    {
        echo '<li id="' . $this->cssId . '">';
        echo '<a href="' . $this->getLink() . '" target="_self">' . $this->text . '</a></li>' . "\n";
    }

}

/**
 *  SideMenu class
 *     this class display side menu item
 *     side menu is mmc's left menu, it regroups
 *     possible actions we can do in a spécific module
 *     like index/configuration/add machine/ add share in
 *     samba module
 *     this class require SideMenuItem
 */
class SideMenu
{
    public $itemArray;
    public $className;
    public $backgroundImage;
    public $activatedItem;

    /**
     *  SideMenu default constructor
     *     initalize empty itemArray for SideMenuItem
     */
    public function __construct()
    {
        $this->itemArray = array();
        $this->backgroundImage = null;
        $this->activatedItem = null;
    }

    /**
     *  add a sideMenu Item into the SideMenu
     * @param $objSideMenuItem object SideMenuItem
     */
    public function addSideMenuItem($objSideMenuItem)
    {
        $this->itemArray[] = &$objSideMenuItem;
    }

    /**
     * CSS class
     */
    public function setClass($class)
    {
        $this->className = $class;
    }

    /**
     * @return className for CSS
     */
    public function getClass()
    {
        return $this->className;
    }

    /**
     * Set the sidemenu background image
     */
    public function setBackgroundImage($bg)
    {
        $this->backgroundImage = $bg;
    }

    /**
     * Get the sidemenu background image
     */
    public function getBackgroundImage()
    {
        return $this->backgroundImage;
    }

    /**
     *  print the SideMenu and the sideMenuItem
     */
    public function display()
    {
        echo "<style>#section {margin-left:200px;}</style>";
        echo "<div id=\"sidebar\">\n";
        echo "<ul class=\"" . $this->className . "\">\n";
        foreach ($this->itemArray as $objSideMenuItem) {
            $objSideMenuItem->display();
        }
        echo "</ul><div class=\"clearer\"></div></div>";
    }

    /**
     *  @return return the Css content for a sidebar
     *  static method to get SideBarCss String
     */
    public function getSideBarCss()
    {
        $css = "";
        foreach ($this->itemArray as $objSideMenuItem) {
            $active = (($objSideMenuItem->submod == $_GET["submod"]) && (($objSideMenuItem->action == $_GET["action"]) || ($objSideMenuItem->action == $this->activatedItem)));
            $css = $css . $objSideMenuItem->getCss($active);
        }
        if ($this->backgroundImage) {
            $css .= "#sectionContainer { background-image: url(" . $this->backgroundImage . ") }";
        }
        return $css;
    }

    /**
     * Force a menu item to be displayed as activated
     * Useful for pages that don't have a dedicated tab
     */
    public function forceActiveItem($item)
    {
        $this->activatedItem = $item;
    }

}

/**
 *  PageGenerator class
 */
class PageGenerator
{
    public $sidemenu;  /* < SideMenu Object */
    public $content;   /* < array who contains contents Objects */

    /**
     *  Constructor
     */
    public function __construct($title = "")
    {
        $content = array();
        $this->title = $title;
    }

    /**
     *  set the sideMenu object
     */
    public function setSideMenu($objSideMenu)
    {
        $this->sidemenu = $objSideMenu;
    }

    /**
     * Set the page title
     */
    public function setTitle($title)
    {
        $this->title = $title;
    }

    /**
     *  display the whole page
     */
    public function display()
    {
        $this->displaySideMenu();
        if ($this->title) {
            $this->displayTitle();
        }
    }

    public function displayCss()
    {
        echo'<style type="text/css">' . "\n";
        echo '<!--' . "\n";
        echo $this->sidemenu->getSideBarCss();
        echo '-->' . "\n";
        echo '</style>' . "\n\n";
    }

    /**
     *  display the side Menu
     */
    public function displaySideMenu()
    {
        if ($this->sidemenu) {
            $this->displayCss();
            $this->sidemenu->display();
        }
    }

    /**
     *  display the page title
     */
    public function displayTitle()
    {
        if (isset($this->title)) {
            print "<h2>" . $this->title . "</h2>\n";
        }
    }

    /**
     * Sometimes, we don't want to add the fixheight div in the page
     */
    public function setNoFixHeight()
    {
        $this->fixheight = false;
    }

}

/**
 * Little wrapper that just include a PHP file as a HtmlElement
 */
class DisplayFile extends HtmlElement
{
    public function __construct($file)
    {
        parent::__construct();
        $this->file = $file;
    }

    public function display($arrParam = array())
    {
        require($this->file);
    }

}

/**
 * Class for a tab content
 */
class TabbedPage extends Div
{
    public function __construct($title, $file)
    {
        parent::__construct(array("class" => "tabdiv"));

        $this->title = $title;
        $this->add(new DisplayFile($file));
    }

    public function displayTitle()
    {
        return "<h2>" . $this->title . "</h2>\n";
    }

    public function begin()
    {
        $s = Div::begin();
        $s .= $this->displayTitle();
        return $s;
    }

}

/**
 * Class for tab displayed by TabSelector
 */
class TabWidget extends HtmlElement
{
    public function __construct($id, $title, $params = array())
    {
        $this->id = $id;
        $this->title = $title;
        $this->params = $params;
        $this->active = false;
        $this->last = false;
    }

    public function getLink()
    {
        return urlStr($_GET["module"] . "/" . $_GET["submod"] . "/" . $_GET["action"], array_merge(array("tab" => $this->id), $this->params));
    }

    public function setActive($flag)
    {
        $this->active = $flag;
    }

    public function display($arrParam = array())
    {
        if ($this->active) {
            $klass = ' class="tabactive"';
        } else {
            $klass = "";
        }
        print '<li id="' . $this->id . '"' . $klass . '"> '
                . '<a href="' . $this->getLink() . '">'
                . $this->title . "</a></li>";
    }

}

/**
 * This class allow to create a page with a tab selector
 */
class TabbedPageGenerator extends PageGenerator
{
    public function __construct()
    {
        parent::__construct();
        $this->topfile = null;
        $this->tabselector = new TabSelector();
        $this->pages = array();
        $this->firstTabActivated = false;
        $this->description = false;
    }

    /**
     * add a header above the tab selector
     */
    public function addTop($title, $file)
    {
        $this->title = $title;
        $this->topfile = $file;
    }

    public function setDescription($desc)
    {
        $this->description = $desc;
    }

    public function displayDescription()
    {
        if ($this->description) {
            printf('<p>%s</p>', $this->description);
        }
    }

    /**
     * Add a new tab to a page
     *
     * @param name: the tab id
     * @param title: the tab title in the tab selector
     * @param pagetitle: the page title
     * @param file: the file that renders the page
     * @param params: an array of URL parameters
     */
    public function addTab($id, $tabtitle, $pagetitle, $file, $params = array())
    {
        global $tabAclArray;
        if (hasCorrectTabAcl($_GET["module"], $_GET["submod"], $_GET["action"], $id)) {
            if (isset($_GET["tab"]) && $_GET["tab"] == $id) {
                $this->tabselector->addActiveTab($id, $tabtitle, $params);
            } else {
                if (isset($_GET["tab"])) {
                    $this->tabselector->addTab($id, $tabtitle, $params);
                } else {
                    if (!$this->firstTabActivated) {
                        $this->tabselector->addActiveTab($id, $tabtitle, $params);
                        $this->firstTabActivated = true;
                    } else {
                        $this->tabselector->addTab($id, $tabtitle, $params);
                    }
                }
            }
            $this->pages[$id] = array($pagetitle, $file);
        }
    }

    public function display()
    {
        $this->page = null;
        $this->displaySideMenu();
        $this->displayTitle();
        $this->displayDescription();
        if ($this->topfile) {
            require($this->topfile);
        }
        $this->tabselector->display();
        if (isset($_GET["tab"]) && isset($this->pages[$_GET["tab"]])) {
            list($title, $file) = $this->pages[$_GET["tab"]];
            $this->page = new TabbedPage($title, $file);
        } else {
            /* Get the first tab page */
            $tab = $this->tabselector->getDefaultTab();
            if ($tab != null) {
                list($title, $file) = $this->pages[$tab->id];
                $this->page = new TabbedPage($title, $file);
            }
        }
        if ($this->page != null) {
            $this->page->display();
        }
    }

}

/**
 * Allow to draw a tab selector
 */
class TabSelector extends HtmlContainer
{
    public function __construct()
    {
        parent::__construct();
        $this->tabs = array();
        $this->order = array();
    }

    public function getDefaultTab()
    {
        if (empty($this->elements)) {
            return null;
        } else {
            return $this->elements[0];
        }
    }

    public function addActiveTab($name, $title, $params = array())
    {
        $tab = new TabWidget($name, $title, $params);
        $tab->setActive(true);
        $this->add($tab);
    }

    public function addTab($name, $title, $params = array())
    {
        $this->add(new TabWidget($name, $title, $params));
    }

    public function begin()
    {
        return '<div class="tabselector"><ul>';
    }

    public function end()
    {
        return "</ul></div>";
    }

}

/**
 * display popup window if notify add in queue
 *
 */
class NotifyWidget
{
    public $id;
    public $strings;
    public $level;
    /**
     * default constructor
     */
    public function __construct($save = true)
    {
        $this->id = uniqid();
        $this->strings = array();
        // 0: info (default, blue info bubble)
        // 1: error for the moment (red icon)
        // 5 is critical
        $this->level = 0;
        if ($save) {
            $this->save();
        }
    }

    /**
     * Save the object in the session
     */
    public function save()
    {
        if (!isset($_SESSION["notify"])) {
            $_SESSION["notify"] = array();
        }
        if ($this->strings) {
            $_SESSION["notify"][$this->id] = serialize($this);
        }
    }

    public function setSize()
    {
        // Deprecated
        return;
    }

    public function setLevel($level)
    {
        $this->level = $level;
    }

    /**
     * Add a string in notify widget
     * @param $str any HTML CODE
     */
    public function add($str, $save = true)
    {
        $this->strings[] = $str;
        if ($save) {
            $this->save();
        }
    }

    public function getImgLevel()
    {
        if ($this->level != 0) {
            return "img/common/icn_alert.gif";
        } else {
            return "img/common/big_icn_info.png";
        }
    }

    public static function begin()
    {
        return '<div style="padding: 10px">';
    }

    public function content()
    {
        $str = '<div style="width: 50px; padding-top: 15px; float: left; text-align: center"><img src="' . $this->getImgLevel() . '" /></div><div style="margin-left: 60px">';
        foreach ($this->strings as $string) {
            $str .= $string;
        }
        $str .= '</div>';
        return $str;
    }

    public static function end()
    {
        $str = '<div style="clear: left; text-align: right; margin-top: 1em;"><button class="btn btn-small" onclick="closePopup()">' . _("Close") . '</button></div></div>';
        return $str;
    }

    public function flush()
    {
        unset($_SESSION["notify_render"][$this->id]);
    }

}

/**
 * display a popup window with a message for a successful operation
 *
 */
class NotifyWidgetSuccess extends NotifyWidget
{
    public function __construct($message)
    {
        // parent::NotifyWidget();
        parent::__construct();
        $this->add("<div class=\"alert alert-success\">$message</div>");
    }

}

/**
 * display a popup window with a message for a failure
 *
 */
class NotifyWidgetFailure extends NotifyWidget
{
    public function __construct($message)
    {
        parent::__construct();
        // parent::NotifyWidget();
        $this->add("<div class=\"alert alert-error\">$message</div>");
        $this->level = 4;
        $this->save();
    }

}

/**
 * display a popup window with a message for a warning
 *
 */
class NotifyWidgetWarning extends NotifyWidget
{
    public function __construct($message)
    {
        // parent::NotifyWidget();
        parent::__construct();

        $this->add("<div class=\"alert\">$message</div>");
        $this->level = 3;
        $this->save();
    }

}

/**
 * Display a simple DIV with a message
 */
class Message extends HtmlElement
{
    public function __construct($msg, $type = "info")
    {
        $this->msg = $msg;
        $this->type = $type;
    }

    public function display($arrParam = array())
    {
        print '<div class="alert alert-' . $this->type . '">' . $this->msg . '</div>';
    }

}

class ErrorMessage extends Message
{
    public function __construct($msg)
    {
        parent::__construct($msg, "error");
    }

}

class SuccessMessage extends Message
{
    public function __construct($msg)
    {
        parent::__construct($msg, "success");
    }

}

class WarningMessage extends Message
{
    public function __construct($msg)
    {
        parent::__construct($msg, "warning");
    }

}

/**
 * Create an URL
 *
 * @param $link string accept format like "module/submod/action" or
 *              "module/submod/action/tab"
 * @param $param assoc array with param to add in GET method
 * @param $ampersandEncode bool defining if we want ampersand to be encoded in URL
 */
function urlStr($link, $param = array(), $ampersandEncode = true)
{
    $arr = array();
    $arr = explode('/', $link);

    if ($ampersandEncode) {
        $amp = "&amp;";
    } else {
        $amp = "&";
    }

    $enc_param = "";
    foreach ($param as $key => $value) {
        $enc_param .= "$amp" . "$key=$value";
    }
    if (safeCount($arr) == 3) {
        $ret = "main.php?module=" . $arr[0] . "$amp" . "submod=" . $arr[1] . "$amp" . "action=" . $arr[2] . $enc_param;
    } elseif (safeCount($arr) == 4) {
        $ret = "main.php?module=" . $arr[0] . "$amp" . "submod=" . $arr[1] . "$amp" . "action=" . $arr[2] . "$amp" . "tab=" . $arr[3] . $enc_param;
    } else {
        die("Can't build URL");
    }

    return $ret;
}

function urlStrRedirect($link, $param = array())
{
    return(urlStr($link, $param, false));
}

function findInSideBar($sidebar, $query)
{
    foreach ($sidebar['content'] as $arr) {
        if (preg_match("/$query/", $arr['link'])) {
            return $arr['text'];
        }
    }
}

function findFirstInSideBar($sidebar)
{
    return $sidebar['content'][0]['text'];
}

class HtmlElement
{
    public $options;

    public function __construct()
    {
        $this->options = array();
    }

    public function setOptions($options)
    {
        $this->options = $options;
    }

    public function hasBeenPopped()
    {
        return true;
    }

    public function display($arrParam = array())
    {
        die("Must be implemented by the subclass");
    }

}

class HtmlContainer
{
    public $elements;
    public $index;
    public $popped;
    public $debug;

    public function __construct()
    {
        $this->elements = array();
        $this->popped = false;
        $this->index = -1;
    }

    public function begin()
    {
        die("Must be implemented by the subclass");
    }

    public function end()
    {
        die("Must be implemented by the subclass");
    }

    public function display()
    {
        print "\n" . $this->begin() . "\n";
        foreach ($this->elements as $element) {
            $element->display();
        }
        print "\n" . $this->end() . "\n";
    }

    public function add($element, $options = array())
    {
        $element->setOptions($options);
        $this->push($element);
    }

    public function push($element)
    {
        if ($this->index == -1) {
            /* Add first element to container */
            $this->index++;
            $this->elements[$this->index] = $element;
        //print "pushing " . $element->options["id"] . " into " . $this->options["id"] . "<br>";
        } else {
            if ($this->elements[$this->index]->hasBeenPopped()) {
                /* All the contained elements have been popped, so add the new element in the list */
                $this->index++;
                $this->elements[$this->index] = $element;
            //print "pushing " . $element->options["id"] . " into " . $this->options["id"] . "<br>";
            } else {
                /* Recursively push a new element into the container */
                $this->elements[$this->index]->push($element);
            }
        }
    }

    public function hasBeenPopped()
    {

        if ($this->popped) {
            $ret = true;
        } elseif ($this->index == -1) {
            $ret = false;
        } else {
            $ret = false;
        }
        return $ret;
    }

    public function pop()
    {
        if (!$this->popped) {
            if ($this->index == -1) {
                $this->popped = true;
            } elseif ($this->elements[$this->index]->hasBeenPopped()) {
                $this->popped = true;
            } else {
                $this->elements[$this->index]->pop();
            }
        //if ($this->popped) print "popping " . $this->options["id"] . "<br>";
        } else {
            die("Nothing more to pop");
        }
    }

}

class Div extends HtmlContainer
{
    public function __construct($options = array(), $class = null)
    {
        //$this->HtmlContainer();
        parent::__construct();
        $this->name = $class;
        $this->options = $options;
        $this->display = true;
    }

    public function begin()
    {
        $str = "";
        foreach ($this->options as $key => $value) {
            $str .= " $key=\"$value\"";
        }
        if (!$this->display) {
            $displayStyle = ' style =" display: none;"';
        } else {
            $displayStyle = "";
        }
        return "<div$str$displayStyle>";
    }

    public function end()
    {
        return "</div>";
    }

    public function setVisibility($flag)
    {
        $this->display = $flag;
    }

}

class Form extends HtmlContainer
{
    public function __construct($options = array())
    {
        parent::__construct();

        if (!isset($options["method"])) {
            $options["method"] = "post";
        }
        if (!isset($options["id"])) {
            $options["id"] = "Form";
        }
        $this->options = $options;
        $this->buttons = array();
        $this->summary = null;
    }

    public function begin()
    {
        $str = "";
        foreach ($this->options as $key => $value) {
            $str .= " $key=\"$value\"";
        }
        $ret = "<form$str>";
        if (isset($this->summary)) {
            $ret = "<p>" . $this->summary . "</p>\n" . $ret;
        }
        return $ret;
    }

    public function end()
    {
        $str = '<input type="hidden" name="auth_token" value="' . $_SESSION['auth_token'] . '">'."\n";
        foreach ($this->buttons as $button) {
            $str .= "\n$button\n";
        }
        $str .= "\n</form>\n";
        return $str;
    }

    public function addButton($name, $value, $klass = "btnPrimary", $extra = "", $type = "submit")
    {
        $b = new Button();
        $this->buttons[] = $b->getButtonString($name, $value, $klass, $extra, $type);
    }

    public function addValidateButton($name)
    {
        $b = new Button();
        $this->buttons[] = $b->getValidateButtonString($name);
    }

    public function addCancelButton($name)
    {
        $b = new Button();
        $this->buttons[] = $b->getCancelButtonString($name);
    }

    public function addExpertButton($name, $value)
    {
        $d = new DivExpertMode();
        $b = new Button();
        $this->buttons[] = $d->begin() . $b->getButtonString($name, $value) . $d->end();
    }

    public function addSummary($msg)
    {
        $this->summary = $msg;
    }

    public function getButtonString($name, $value, $klass = "btnPrimary", $extra = "", $type = "submit")
    {
        $b = new Button();
        return $b->getButtonString($name, $value, $klass, $extra, $type);
    }

    public function addOnClickButton($text, $url)
    {
        $b = new Button();
        $this->buttons[] = $b->getOnClickButton($text, $url);
    }

}

class Button
{
    public function __construct($module = null, $submod = null, $action = null) # TODO also verify ACL on tabs
    {
        if ($module == null) {
            $this->module = $_GET["module"];
        } else {
            $this->module = $module;
        }
        if ($submod == null) {
            $this->submod = $_GET["submod"];
        } else {
            $this->submod = $submod;
        }
        if ($action == null) {
            $this->action = $_GET["action"];
        } else {
            $this->action = $action;
        }
    }

    public function getButtonString($name, $value, $klass = "btnPrimary", $extra = "", $type = "submit")
    {
        if (hasCorrectAcl($this->module, $this->submod, $this->action)) {
            return $this->getButtonStringWithRight($name, $value, $klass, $extra, $type);
        } else {
            return $this->getButtonStringWithNoRight($name, $value, $klass, $extra, $type);
        }
    }

    public function getButtonStringWithRight($name, $value, $klass = "btnPrimary", $extra = "", $type = "submit")
    {
        return "<input type=\"$type\" name=\"$name\" value=\"$value\" class=\"$klass\" $extra />";
    }

    public function getButtonStringWithNoRight($name, $value, $klass = "btnPrimary", $extra = "", $type = "submit")
    {
        return "<input disabled type=\"$type\" name=\"$name\" value=\"$value\" class=\"btnDisabled\" $extra />";
    }

    public function getValidateButtonString($name, $klass = "btnPrimary", $extra = "", $type = "submit")
    {
        return $this->getButtonString($name, _("Confirm"), $klass);
    }

    public function getCancelButtonString($name, $klass = "btnSecondary", $extra = "", $type = "submit")
    {
        return $this->getButtonString($name, _("Cancel"), $klass);
    }

    public function getOnClickButton($text, $url, $klass = "btnPrimary", $extra = "", $type = "button")
    {
        return $this->getButtonString("onclick", $text, $klass, $extra = "onclick=\"location.href='" . $url . "';\"", $type);
    }

}

class ValidatingForm extends Form
{
    public function __construct($options = array())
    {
        parent::__construct($options);

        $this->options["onsubmit"] = "return validateForm('" . $this->options["id"] . "');";
    }

    public function end()
    {
        $str = parent::end();
        $str .= "
        <script type=\"text/javascript\">
            jQuery('#" . $this->options["id"] . ":not(.filter) :input:visible:enabled:first').focus();
        </script>\n";
        return $str;
    }

}

/**
 *
 * Allow to easily build the little popup displayed when deleting a user for example
 *
 */
class PopupForm extends Form
{
    public function __construct($title, $id = 'Form')
    {
        $options = array("action" => $_SERVER["REQUEST_URI"], 'id' => $id);
        parent::__construct($options);

        $this->title = $title;
        $this->text = array();
        $this->ask = "";
    }

    public function begin()
    {
        $str = "<h2>" . $this->title . "</h2>\n";
        $str .= parent::begin();
        foreach ($this->text as $text) {
            $str .= "<p>" . $text . "</p>";
        }
        return $str;
    }

    public function end()
    {
        $str = "<p>" . $this->ask . "</p>";
        $str .= parent::end();
        return $str;
    }

    public function addText($msg)
    {
        $this->text[] = $msg;
    }

    public function setQuestion($msg)
    {
        $this->ask = $ask;
    }

    public function addValidateButtonWithFade($name)
    {
        $this->buttons[] = $this->getButtonString($name, _("Confirm"), "btnPrimary", "onclick=\"closePopup(); return true;\"");
    }

    public function addCancelButton($name)
    {
        $this->buttons[] = $this->getButtonString($name, _("Cancel"), "btnSecondary", "onclick=\"closePopup(); return false;\"");
    }

}

/**
 *
 * Allow to easily build the little popup, summon a new window
 *
 */
class PopupWindowForm extends PopupForm
{
    public function __construct($title)
    {
        $options = array("action" => $_SERVER["REQUEST_URI"]);
        parent::__construct($options);
        $this->title = $title;
        $this->text = array();
        $this->ask = "";
        $this->target_uri = "";
    }

    public function addValidateButtonWithFade($name)
    {
        $this->buttons[] = $this->getButtonString($name, _("Confirm"), "btnPrimary", "onclick=\"jQuery('popup').fadeOut(); window.open('" . $this->target_uri . "', '', 'toolbar=no, location=no, menubar=no, status=no, status=no, scrollbars=yes, width=330, height=200'); return false;\"");
    }

}

class Table extends HtmlContainer
{
    public function __construct($options = array())
    {
        parent::__construct();
        $this->lines = array();
        $this->tr_style = '';
        $this->td_style = '';
        $this->options = $options;
        if (isset($options['tr_style'])) {
            $this->tr_style = $options['tr_style'];
        }
        if (isset($options['td_style'])) {
            $this->td_style = $options['td_style'];
        }
    }

    public function setLines($lines)
    {
        $this->lines = $lines;
    }

    public function begin()
    {
        return '<table cellspacing="0">';
    }

    public function end()
    {
        return "</table>";
    }

    public function getContent()
    {
        $str = '';
        foreach ($this->lines as $line) {
            $str .= sprintf("<tr%s><td%s>%s</td></tr>", $this->tr_style, $this->td_style, implode(sprintf('</td><td%s>', $this->td_style), $line));
        }
        return $str;
    }

    public function displayTable($displayContent = false)
    {
        print $this->begin();
        if ($displayContent) {
            print $this->getContent();
        }
        print $this->end();
    }

}

class DivForModule extends Div
{
    public function __construct($title, $color, $options = array())
    {
        $options["style"] = "background-color: " . $color;
        $options["class"] = "formblock";
        parent::__construct($options);
        $this->title = $title;
        $this->color = $color;
    }

    public function begin()
    {
        print parent::begin();
        print "<h3>" . $this->title . "</h3>";
    }

}

class DivExpertMode extends Div
{
    public function begin()
    {
        $str = '<div id="expertMode" ';
        if (isExpertMode()) {
            $str .= ' style="display: inline;"';
        } else {
            $str .= ' style="display: none;"';
        }
        return $str . ' >';
    }

}

class ModuleTitleElement extends HtmlElement
{
    public function __construct($title)
    {
        $this->title = $title;
    }

    public function display($arrParam = array())
    {
        print '<br><h1>' . $this->title . '</h1>';
    }

}

class TitleElement extends HtmlElement
{
    public function __construct($title, $level = 2)
    {
        $this->title = $title;
        $this->level = $level;
    }

    public function display($arrParam = array())
    {
        print '<br/><h' . $this->level . '>' . $this->title . '</h' . $this->level . '>';
    }

}

class SpanElement extends HtmlElement
{
    public function __construct($content, $class = null)
    {
        $this->name = $class;
        $this->content = $content;
        $this->class = $class;
    }

    public function display($arrParam = array())
    {
        if ($this->class) {
            $class = ' class="' . $this->class . '"';
        } else {
            $class = '';
        }
        printf('<span%s>%s</span>', $class, $this->content);
    }
}

class ParaElement extends HtmlElement
{
    public function __construct($content, $class = null)
    {
        $this->name = $class;
        $this->content = $content;
        $this->class = $class;
    }

    public function display($arrParam = array())
    {
        if ($this->class) {
            $class = ' class="' . $this->class . '"';
        } else {
            $class = '';
        }
        printf('<p%s>%s</p>', $class, $this->content);
    }

}

class SelectElement extends HtmlElement
{
    public function __construct($name, $nametab)
    {
        $this->name = $name;
        $this->nametab = $nametab;
    }

    public function display($arrParam = array())
    {
        $p = new ParaElement('<a href="javascript:void(0);" onclick="checkAll(this, \'' . $this->name . '\',1); checkAll(this, \'' . $this->nametab . '\',1);">' . _("Select all") . ' </a> / <a href="javascript:void(0);" onclick="checkAll(this, \'' . $this->name . '\',0); checkAll(this, \'' . $this->nametab . '\',0);">' . _("Unselect all") . '</a>');
        $p->display();
    }

}

class TrTitleElement extends HtmlElement
{
    public function __construct($arrtitles)
    {
        $this->titles = $arrtitles;
    }

    public function display($arrParam = array())
    {
        $colsize = 100 / sizeof($this->titles);
        print '<tr>';
        foreach ($this->titles as $value) {
            print '<td width="' . $colsize . '%"><b>' . $value . '</b></td>';
        }
        print '</tr>';
    }

}

class AjaxPage extends HtmlElement
{
    public function __construct($url, $id = "container", $params = array(), $refresh = 10)
    {
        $this->url = $url;
        $this->id = $id;
        $this->class = "";
        $this->params = json_encode($params);
        $this->refresh = $refresh;
    }

    public function display($arrParam = array())
    {
        echo <<< EOT
        <div id="{$this->id}" class="{$this->class}"></div>
        <script type="text/javascript">
        function update_{$this->id}(){
            jQuery.ajax({
                'url': '{$this->url}',
                type: 'get',
                data: {$this->params},
                success: function(data){
                    jQuery("#{$this->id}").html(data);
                    setTimeout('update_{$this->id}()',1000*{$this->refresh});
                }
            });
        }
        update_{$this->id}();

        </script>
EOT;
    }

}

class medulla_progressbar extends HtmlElement
{
    private static $scriptIncluded = false;
    /** @var int $value Valeur de la barre de progression (entre 0 et 100). */
    private $value;

    /** @var string $cssClass Nom de la classe CSS pour la barre de progression. */
    protected $cssClass = 'progressbar_med';

    /** @var string $dataValue Valeur de l'attribut data-value. */
    private $dataValue;

    /** @var string $title Valeur de l'attribut title. */
    private $title;

    /**
     * Constructeur de la classe.
     *
     * @param int $value Valeur initiale de la barre de progression (0-100).
     * @param string $dataValue Valeur de l'attribut data-value.
     * @param string $title Valeur de l'attribut title.
     */
    public function __construct($value, $dataValue = "", $title = "")
    {
        parent::__construct();
        // Assure que la valeur reste entre 0 et 100
        $this->value = max(0, min(100, (int)$value));
        $this->dataValue = $dataValue;
        $this->title = $title;
        if (!self::$scriptIncluded) {
            $this->includeScript();
            self::$scriptIncluded = true;
        }
    }

    /**
     * Affiche la barre de progression sous forme de code HTML.
     *
     * @param array $arrParam Paramètres optionnels (non utilisés ici).
     */
    public function display($arrParam = array())
    {
        // echo $this->toString();
        echo $this->my_string();
    }

    /**
     * Retourne une chaîne de caractères représentant la barre de progression.
     *
     * @return string Chaîne de caractères de la barre de progression.
     */
    public function my_string()
    {
        return $this->generateHtml();

    }

    /**
     * Retourne le code HTML de la barre de progression.
     *
     * @return string HTML de la barre de progression.
     */
    public function __toString()
    {
        return $this->generateHtml();
    }

   private function toString() {
        // Retourne une représentation sous forme de chaîne de caractères de l'objet
        return $this->generateHtml();
    }
    /**
     * Génère le code HTML de la barre de progression.
     *
     * @return string HTML de la barre de progression.
     */
    private function generateHtml()
    {
        $titleAttr = !empty($this->title) ? ' title="' . htmlspecialchars($this->title, ENT_QUOTES, 'UTF-8') . '"' : '';
        $dataValueAttr = !empty($this->dataValue) ? ' data-value="' . htmlspecialchars($this->dataValue, ENT_QUOTES, 'UTF-8') . '"' : '';

        return str_replace(array("\r", "\n"), ' ', '<div class="' . $this->cssClass . '">
                    <span class="value_progress"' . $titleAttr . ' style="display: none;"' . $dataValueAttr . '>' . (string)$this->value . '</span>
                </div>');
    }

    private function includeScript() {
        echo <<<EOT
<script type="text/javascript">
    /**
     * Fonction qui renvoie une couleur intermédiaire entre rouge, jaune et vert en fonction d'une valeur de 0 à 100.
     * @param {number} value - Valeur entre 0 et 100.
     * @return {string} - Couleur au format RGB.
     */
    function getColor(value) {
        // Assure que la valeur est entre 0 et 100
        value = Math.max(0, Math.min(100, value));
        let r, g, b;

        if (value < 50) {
            // Interpolation entre rouge (0%) et jaune (50%)
            r = 255;
            g = Math.round((255 * value) / 50);
            b = 0;
        } else {
            // Interpolation entre jaune (50%) et vert (100%)
            r = Math.round(255 * (1 - (value - 50) / 50));
            g = 255;
            b = 0;
        }
        // Retourne la couleur au format RGB string
        return 'rgb('+r+','+g+','+b+')';
    }

    jQuery(document).ready(function() {
        // console.log("Le script est inclus une seule fois par page. URL: " + window.location.href);

        jQuery(".progressbarstaticvalue_med").each(function() {
            // Récupère l'élément <span> enfant avec la classe "value_progress"
            let spanChild = jQuery(this).find(".value_progress");

            // Récupère la valeur cachée de la barre de progression
            let spanInteger = parseInt(spanChild.text(), 10) || 0; // Convertit en entier
            let spanIntegertrue = spanInteger; // Convertit en entier sécurisé

            // Récupère la couleur en fonction de la valeur
            let colorgraph = getColor(spanInteger);

            // Récupère les valeurs des attributs data-value et title
            let spanValueData = spanChild.attr('data-value') || '';

            let spanTitle = spanChild.attr('title') || '';

            // Ajoute l'attribut title au <div> parent si présent
            if (spanChild.length > 0 && spanChild.attr('title')) {
                jQuery(this).attr('title', spanTitle);
            }

            // Initialise la barre de progression jQuery UI avec la valeur récupérée
            jQuery(this).progressbar({ value: 100 });
            jQuery(this).find(".ui-progressbar-value")
                .css({
                    "background": colorgraph, // Si valeur == 0, barre grise
                    "color": spanInteger >= 30 && spanInteger <= 70 ? "#000" : "#fff", // Couleur du texte en noir si entre 30 et 70, sinon blanc
                    "text-align": "center", // Centre le texte
                    "line-height": "20px", // Ajuste la hauteur pour aligner le texte verticalement
                    "border-radius": "5px"
                })
                .attr("data-value", spanInteger); // Ajoute un attribut data pour stockage

            // Applique un style à la barre de progression vide (fond)
            jQuery(this).find(".ui-progressbar")
                .css({
                    "background-color": "transparent", // Fond transparent
                    "border-radius": "5px", // Coins arrondis
                    "height": "15px", // Hauteur de la barre
                    "border": "1px solid #999" // Bordure grise
                });

            // Définit le texte de la barre de progression
            jQuery(this).find(".ui-progressbar-value").text(spanValueData + " " + spanIntegertrue + "%");
        });
        jQuery(".progressbar_med").each(function() {
            // Récupère la valeur cachée de la barre de progression
            let spanChild = jQuery(this).find(".value_progress");
            let spanInteger = parseInt(spanChild.text(), 10) || 0; // Convertit en entier
            let spanIntegertrue = spanInteger; // Convertit en entiersécurisé
            // Détermine la couleur de fin en fonction de la valeur
            let startcolor = "#FF0000"; // Rouge par défaut
            let endcolor = "#FF0000"; // Rouge par défaut
            if (spanInteger >= 25) endcolor = "#e2a846"; // Orange
            if (spanInteger >= 50) endcolor = "#f4f529"; // Jaune
            if (spanInteger >= 75) endcolor = "#bcf529"; // Vert clair
            if (spanInteger >= 90) endcolor = "#02ab17"; // Vert foncé
            // Déclare la variable backgroundinput
            let backgroundinput = 0;

            // Si la valeur est inférieure à 20, change la couleur et définit la barre à 100%
            if (spanInteger < 20) {
                backgroundinput = 1; // Utilise directement la variable globale
                endcolor = "red"; // Fixe la couleur rouge
                startcolor= "red";
                spanInteger = 100; // Définit la valeur à 100%
            }
            if (spanInteger == 20) {
                backgroundinput = 1; // Utilise directement la variable globale
                endcolor = "green"; // Fixe la couleur rouge
                startcolor= "green";
                spanInteger = 100; // Définit la valeur à 100%
            }
            // Initialise la barre de progression jQuery UI avec la valeur récupérée
            jQuery(this).progressbar({ value: spanInteger });
            // Applique un dégradé de couleur sur la partie remplie de la barre de progression
            jQuery(this).find(".ui-progressbar-value")
                .css({
                    "background": spanInteger > 0 ? "linear-gradient(to right," + startcolor + ", " + endcolor + ")" : "#ccc", // Si valeur == 0, barre grise
                    "color": "#fff", // Couleur du texte en blanc
                    "text-align": "center", // Centre le texte
                    "line-height": "20px", // Ajuste la hauteur pour aligner le texte verticalement
                    "border-radius": "5px"
                })
                .attr("data-value", spanInteger); // Ajoute un attribut data pour stockage

            // Applique un style à la barre de progression vide (fond)
            jQuery(this).find(".ui-progressbar")
                .css({
                    "background-color": "transparent", // Fond transparent
                    "border-radius": "5px", // Coins arrondis
                    "height": "15px", // Hauteur de la barre
                    "border": "1px solid #999" // Bordure grise
                });

            // Si la condition de fond est remplie, affiche "0%", sinon affiche la valeur
            if (backgroundinput == 1) {
                jQuery(this).find(".ui-progressbar-value").text(spanIntegertrue+ "%");
            } else {
                jQuery(this).find(".ui-progressbar-value").text(spanInteger + "%");
            }
        });
    });
</script>
EOT;
    }
}

class medulla_progressbar_static extends medulla_progressbar
{
    /**
     * Constructeur de la classe.
     *
     * @param int $value Valeur initiale de la barre de progression (0-100).
     * @param string $dataValue Valeur de l'attribut data-value.
     * @param string $title Valeur de l'attribut title.
     */
    public function __construct($value, $dataValue = "", $title = "")
    {
        parent::__construct($value, $dataValue, $title);
        // Modifie la classe CSS pour la barre de progression statique
        $this->cssClass = 'progressbarstaticvalue_med';
    }
}
?>

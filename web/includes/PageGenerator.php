<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2010 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

require ("FormGenerator.php");

/**
 * return an uniqId (use full for javascript auto generation
 */
function getUniqId() {
    global $__uniqID;
    $__uniqID++;
    return $__uniqID;
}

/**
 * can echo obj and string with the same function
 * similar to "echo" in PHP5
 */
function echo_obj($obj) {

   if (is_object($obj)){
        echo $obj->__toString();
   }
   else if(is_bool($obj)) {
        if($obj)
            echo '<img src="img/common/icn_yes.gif" alt="yes" />';
   }
   else {
        echo ($obj);
   }

}

/**
 * class for action encapsulation
 * Abstract class for the moment
 * @see EditInPlace
 */
class ActionEncapsulator {
    function ActionEncapsulator() {

    }

    function __toString() {
        return "default action encapsulator";
    }
}

/**
 * AutoGenerate an EditInPlace text
 * based on scriptaculous javascript
 */
class EditInPlace extends ActionEncapsulator{

    var $origText;
    var $url;
    var $param;

    function EditInPlace($origText,$url,$param) {
        $this->origText = $origText;
        $this->url = $url;
        $this->param = $param;

    }

    function __toString() {

        $param = array();

        foreach ($this->param as $key=>$value) {
            $param[] = "$key=$value";
        }

        $urlparam = implode("&",$param);

        if ($this->origText== '') {
            $this->origText= "n/a";
        }

        $idx = getUniqId();

        $str = '';
        $str.= "<span id=\"id$idx\" class=\"editinplace\">".$this->origText."</span>";


       $str .= '<script type="text/javascript">';
       $str .= "     new Ajax.InPlaceEditor($('id$idx'),'".$this->url."', {\n
                okButton: true, cancelLink: true, cancelText : '"._('Cancel')."',
                highlightcolor : '#FF9966',
                ajaxOptions: {method: 'get' },\n
                callback: function(form,value) {\n
                    return '$urlparam&value='+value\n
                }\n
            });\n
        </script>\n";
      return $str;
    }

}

/**
 *  class for action in various application
 */
class ActionItem {
    var $desc;
    var $action;
    var $classCss;
    var $paramString;
    var $mod;

    /**
     *  Constructor
     * @param $desc description
     * @param $action string include in the url
     * @param $classCss class for CSS like "supprimer" or other class define
     *    in the CSS global.css
     * @param $paramString add "&$param=" at the very end of the url
     */
    function ActionItem($desc, $action, $classCss, $paramString, $module = null, $submod = null, $tab = null, $mod = false) {
        $this->desc=$desc;
        $this->action=$action;
        $this->classCss=$classCss;
        $this->paramString=$paramString;
        if ($module == null) $this->module = $_GET["module"];
        else $this->module = $module;
        if ($submod == null) $this->submod = $_GET["submod"];
        else $this->submod = $submod;
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
    function display($param, $extraParams = array()) {
        if (hasCorrectAcl($this->module,$this->submod,$this->action)) {
            $this->displayWithRight($param, $extraParams);
        } else {
            $this->displayWithNoRight($param, $extraParams);
        }
    }

    /**
     * display function if you have correct right on this action
     */
    function displayWithRight($param, $extraParams = array()) {
        /* add special param for actionItem */
        if (is_array($extraParams)) {
            $extraParams['mod'] = $this->mod;
        }
        echo "<li class=\"".$this->classCss."\">";
        if (is_array($extraParams) & !empty($extraParams)) $urlChunk = $this->buildUrlChunk($extraParams);
        else $urlChunk = "&amp;" . $this->paramString."=" . rawurlencode($extraParams);
        echo "<a title=\"".$this->desc."\" href=\"" . urlStr($this->path) . $urlChunk . "\">&nbsp;</a>";
        echo "</li>";
    }

    /**
     * display function if you don't have the right for this action
     */
    function displayWithNoRight($param, $extraParams = array()) {
        echo "<li class=\"".$this->classCss."\" style=\"opacity: 0.30;\">";
        echo "<a title=\"".$this->desc."\" href=\"#\" onclick='return false;'>&nbsp;</a>";
        echo "</li>";
    }

    /**
     * transform $obj param in link for this action
     */
    function encapsulate($obj, $extraParams = Array()) {
        if (hasCorrectAcl($this->module,$this->submod,$this->action)) {
            if (is_array($extraParams) & !empty($extraParams)) {
                $urlChunk = $this->buildUrlChunk($extraParams);
            } else {
                $urlChunk = "&amp;" . $this->paramString."=" . rawurlencode($obj);
            }
            $str= "<a title=\"".$this->desc."\" href=\"main.php?module=".$this->module."&amp;submod=".$this->submod."&amp;action=".$this->action . $urlChunk ."\">";
            $str.= trim($obj);
            $str.= "</a>";
            return $str;
        } else {
            $str= "<a title=\"".$this->desc."\" href=\"#\">";
            $str.= "$obj";
            $str.=" </a>";
            return $str;
        }
    }

    /**
     * Build an URL chunk using a array of option => value
     */
    function buildUrlChunk($arr) {
        $urlChunk = "";
        foreach($arr as $option => $value) {
            $urlChunk .= "&amp;" . $option . "=" . urlencode($value);
        }
        return $urlChunk;
    }


    /**
     * display help (not use for the moment)
     */
    function strHelp() {
        $str = "";
        $str.= "<li class=\"".$this->classCss."\">";
        $str.= "<a title=\"".$this->desc."\" href=\"#\">";
        $str.= " </a>".$this->desc."</li>";
        return $str;
    }
}

/**
 * display action in a JavaScript popup
 *
 * @see ActionItem
 * @see showPopup (js)
 */
class ActionPopupItem extends ActionItem {

    function ActionPopupItem($desc, $action, $classCss, $paramString, $module = null, $submod = null, $tab = null, $width = 300, $mod = false) {
        $this->ActionItem($desc, $action, $classCss, $paramString, $module, $submod, $tab, $mod);
        $this->setWidth($width);
    }

    /**
     * Set the JavaScript popup width.
     * The default width value is 300px.
     */
    function setWidth($width) {
        $this->width = $width;
    }

    function displayWithRight($param, $extraParams = array()) {
        /* Add special param for actionPopupItem */
        if (is_array($extraParams)) {
            $extraParams['mod'] = $this->mod;
        }
        if (is_array($extraParams) & !empty($extraParams)) {
            $urlChunk = $this->buildUrlChunk($extraParams);
        } else {
            $urlChunk = "&amp;" . $this->paramString."=" . rawurlencode($param);
        }
        echo "<li class=\"".$this->classCss."\">";
        echo "<a title=\"".$this->desc."\" href=\"main.php?module=".$this->module."&amp;submod=".$this->submod."&amp;action=" . $this->action . $urlChunk . "\"";
        echo " onclick=\"PopupWindow(event,'main.php?module=".$this->module."&amp;submod=".$this->submod."&amp;action=" .$this->action . $urlChunk . "', " . $this->width . "); return false;\">&nbsp;</a>";
        echo "</li>";
    }

    function encapsulate($obj, $extraParams = array()) {
        if (is_array($extraParams) & !empty($extraParams)) {
            $urlChunk = $this->buildUrlChunk($extraParams);
        } else {
            $urlChunk = "&amp;" . $this->paramString."=" . rawurlencode($obj);
        }
        $str= "<a title=\"".$this->desc."\" href=\"main.php?module=".$this->module."&amp;submod=".$this->submod."&amp;action=".$this->action . $urlChunk . "\" ";
        $str.= "  onclick=\"showPopup(event,'main.php?module=".$this->module."&amp;submod=".$this->submod."&amp;action=".$this->action . $urlChunk . "', " . $this->width . "); return false;\">";
        $str.= "$obj";
        $str.=" </a>";
        return $str;
    }
}

class EmptyActionItem extends ActionItem {

    function EmptyActionItem() {
    }

    function display($param = null, $extraParams = Array()) {
        print '<li class="empty"><a href="#" onclick="return false;">&nbsp;</a></li>';
    }

}

/**
 *  class who maintain array presentation of information
 */
class ListInfos extends HtmlElement {
    var $arrInfo; /**< main list */
    var $extraInfo;
    var $paramInfo;
    var $name;
    var $arrAction; /**< list of possible action */
    var $end, $start;

    var $description; /**< list of description (not an obligation) */
    var $col_width; /**< Contains the columns width */
    var $tooltip; /**< Contains the tooltip for column label */

    /**
     * constructor
     * @param $tab must be an array of array
     */
    function ListInfos($tab, $description = "", $extranavbar = "", $width = "", $tooltip = "") {
        $this->arrInfo=$tab;
        $this->arrAction=array();
        $this->description[] = $description;
        $this->extranavbar = $extranavbar;
        $this->initVar();
        $this->col_width = array();
        $this->col_width[] = $width;
        $this->tooltip = array();
        $this->tooltip[] = $tooltip;
        $this->firstColumnActionLink = True;
        $this->_addInfo = array();
    }

    function setAdditionalInfo($addinfo) {
        $this->_addInfo = $addinfo;
    }

    /**
     * Set the number of rows to display per ListInfos page.
     * It overrides the default value defined by $conf["global"]["maxperpage"].
     *
     * @param $value The number of rows
     */
    function setRowsPerPage($value) {
        $this->end = $value;
    }

    /**
     *  add an ActionItem
     *  @param $objActionItem object ActionItem
     */
    function addActionItem($objActionItem) {
        $this->arrAction[] = &$objActionItem;
    }

    /**
     * Add an array of ActionItem
     * Useful if all action items are not the same for each row of the list
     *
     */
    function addActionItemArray($objActionItemArray) {
        assert(is_array($objActionItemArray));
        $this->arrAction[] = &$objActionItemArray;
    }


    /**
     *  add an array String to display
     *  @param $arrString an Array String to display
     *  @param description Table column name
     *  @param width Table column width
     *  @param tooltip Tooltip to display on the column name
     */
    function addExtraInfo($arrString, $description= "", $width="", $tooltip = "") {
        assert(is_array($arrString));
        $this->extraInfo[] = &$arrString;
        $this->description[] = $description;
        $this->col_width[] = $width;
        $this->tooltip[] = $tooltip;
    }

    /**
     *  set parameters array for main action
     *  @param $arrString an Array of string to be used as parameters for the main action
     */
    function setParamInfo($arrString) {
        assert(is_array($arrString));
        $this->paramInfo = $arrString;
    }

    /**
     * Set the left padding of the table header.
     * It will be set to 32 by default
     * @param $padding an integer
     */
    function setTableHeaderPadding($padding) {
        $this->first_elt_padding = $padding;
    }

    /**
     * Disable the link to the first available action in the table
     * This link is always done by default
     */
    function disableFirstColumnActionLink() {
        $this->firstColumnActionLink = False;
    }

    /**
     *  init class' vars
     */
    function initVar() {

        $this->name="Elements";

        global $conf;

	$this->maxperpage = (isset($_REQUEST['maxperpage'])) ? $_REQUEST['maxperpage'] : $conf['global']['maxperpage'];

        if (!isset($_GET["start"])) {
            if (!isset($_POST["start"])) {
                $this->start = 0;

                if (count($this->arrInfo) > 0) {
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
        $this->setNavBar(new SimpleNavBar($this->start, $this->end, count($this->arrInfo), $this->extranavbar));
    }


    /**
     *  set the name of the array (for CSS)
     */
    function setName($name) {
        $this->name=$name;
    }

    /**
     *  set the cssclass of a row
     */
    function setCssClass($name) {
        $this->cssClass=$name;
    }

    /**
     * set a cssclass for each row
     */
    function setCssClasses($a_names) {
        $this->cssClasses = $a_names;
    }
    
    /**
     * set cssclass for each MainAction column
     */
    function setMainActionClasses($classes) {
        $this->mainActionClasses = $classes;
    }    

    /**
     * Set the ListInfos navigation bar
     */
    function setNavBar($navbar) {
        $this->navbar = $navbar;
    }

    /**
     *
     * Display the widget navigation bar if $navbar is True
     *
     * @param $navbar: if $navbar is true the navigation bar is displayed
     */
    function displayNavbar($navbar) {
        if ($navbar) $this->navbar->display();
    }

    /**
     *  draw number of page etc...
     */
    function drawHeader($navbar = 1) {

        $this->displayNavbar($navbar);
        echo "<p class=\"listInfos\">";

        /*
         * Management of the numbers "start" and "end" to display depending on the maxperpage set in the selector
         * These numbers are more user-friendly and do not begin with 0
         */
        echo $this->name." <strong>".min($this->start + 1, count($this->arrInfo)) . "</strong>\n ";
        echo _("to")." <strong>".min($this->end + 1, count($this->arrInfo))."</strong>\n";

        printf (_(" - Total <b>%s </b>")."\n",count($this->arrInfo));
        /* Display page counter only when useful */
        if (count($this->arrInfo) > $this->maxperpage) {
            echo "("._("page")." ";
            printf("%.0f", ($this->end + 1) / $this->maxperpage);
            echo " / ";
            $pages = intval((count($this->arrInfo) / $this->maxperpage)) ;
            if ((count($this->arrInfo) % $this->maxperpage > 0) && (count($this->arrInfo) > $this->maxperpage))
                $pages++;
            else if ((count($this->arrInfo) > 0) && ($pages < 1))
                $pages = 1;
            else if ($pages < 0)
                $pages = 0;
            printf("%.0f", $pages);
            echo ")\n";
        }
        echo "</p>";
    }

    /**
     * display main action (first action
     */
    function drawMainAction($idx) {
        if (!empty($this->cssClass)) {
            echo "<td class=\"".$this->cssClass."\">";
        } else if (!empty($this->mainActionClasses)) {
            echo "<td class=\"".$this->mainActionClasses[$idx]."\">";
        } else {
            echo "<td>";
        }
        if (is_a($this->arrAction[0], 'ActionItem')) {
            $firstAction = $this->arrAction[0];
        } else if (is_array($this->arrAction[0])) {
            $firstAction = $this->arrAction[0][$idx];
        }
        echo $firstAction->encapsulate($this->arrInfo[$idx], $this->paramInfo[$idx]);
        if (isset($this->_addInfo[$idx])) {
            print " " . $this->_addInfo[$idx];
        }
        echo "</td>";
    }

    function drawTable($navbar = 1) {
        echo "<table border=\"1\" cellspacing=\"0\" cellpadding=\"5\" class=\"listinfos\">\n";
        echo "<thead><tr>";
        $first = False;
        foreach ($this->description as $key => $desc) {
            if (isset($this->col_width[$key])) {
                $width_styl = 'width: '.$this->col_width[$key].';';
            } else {
                $width_styl = '';
            }
            if (!$first) {

                if (!isset($this->first_elt_padding)) {
                    $this->first_elt_padding = 32;
                }
                echo "<td style=\"$width_styl\"><span style=\"color: #777; padding-left: ".$this->first_elt_padding."px;\">$desc</span></td>";
                $first = True;

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
                echo "<td style=\"$width_styl\"><span style=\"color: #777;\">$tooltipbegin$desc$tooltipend</span></td>";
            }
        }

        if (count($this->arrAction)!=0) { //if we have actions
            if (!empty($this->col_width)) {
                $width_styl = $this->col_width[count($this->col_width) - 1];
            }
            $width_styl = isset($width_styl) ? sprintf('width: %s;', $width_styl) : '';
            echo "<td style=\"text-align: right; $width_styl\"><span style=\"color: #AAA;\" >Actions</span></td>";
        }

        echo "</tr></thead>";

        for ( $idx = $this->start; ($idx < count($this->arrInfo)) && ($idx <= $this->end); $idx++) {
            if (($this->start - $idx) % 2) {
                echo "<tr";
                if (!empty($this->cssClasses[$idx])) {
                    echo " class=\"".$this->cssClasses[$idx]."\"";
                }
                echo ">";
            } else {
                echo "<tr class=\"alternate";
                if (!empty($this->cssClasses[$idx])) {
                    echo " ".$this->cssClasses[$idx];
                }
                echo "\">";
            }

            //link to first action (if we have an action)
            if (count($this->arrAction) && $this->firstColumnActionLink) {
                $this->drawMainAction($idx);
            } else {
                if (!empty($this->cssClass)) {
                    echo "<td class=\"".$this->cssClass."\">";
                } else if (!empty($this->mainActionClasses)) {
                    echo "<td class=\"".$this->mainActionClasses[$idx]."\">";
                } else {
                    echo "<td>";
                }
                echo $this->arrInfo[$idx];
                echo "</td>";
            }

            if ($this->extraInfo)
                foreach ($this->extraInfo as $arrayTMP) {
                    echo "<td>";
                    if(trim($arrayTMP[$idx]) != "") {
                        echo_obj($arrayTMP[$idx]);
                    }
                    else {
                        echo "&nbsp;";
                    }
                    echo "</td>";
                }
            if (count($this->arrAction)!=0) {
                echo "<td class=\"action\">";
                echo "<ul class=\"action\">";
                foreach ($this->arrAction as $objActionItem) {
                    if (is_a($objActionItem, 'ActionItem')) {
                        $objActionItem->display($this->arrInfo[$idx], $this->paramInfo[$idx]);
                    } else if (is_array($objActionItem)) {
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
            print '$(\'help\').innerHTML=\'\''."\n";
            print '$(\'help\').innerHTML+=\'<ul>\''."\n";
            print '$(\'help\').innerHTML+=\'<li><h3>Aide contextuelle</h3></li>\''."\n";
            foreach ($this->arrAction as $objActionItem) {
                $content = $objActionItem->strHelp();
                print '$(\'help\').innerHTML+=\''.$content.'\';'."\n";
            }
            print '$(\'help\').innerHTML+=\'</ul>\''."\n";
            print '--></script>';
        }

    }

    function display($navbar = 1, $header =1 ) {
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
class OptimizedListInfos extends ListInfos {

    /**
     * Allow to set another item count
     */
    function setItemCount($count) {
        $this->itemCount = $count;
    }

    function getItemCount() {
        return $this->itemCount;
    }

    /**
     *  init class' vars
     */
    function initVar() {
        $this->name="Elements";
        global $conf;
        if (!isset($_GET["start"])) {
            if (!isset($_POST["start"])) {
                $this->start = 0;
                if (count($this->arrInfo) > 0) {
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
        $this->setItemCount(count($this->arrInfo));
        $this->startreal = $this->start;
        $this->endreal = $this->end;
    }

    /**
     *  draw number of page etc...
     */
    function drawHeader($navbar=1) {
        $count = $this->getItemCount();
        $this->displayNavbar($navbar);
        echo "<p class=\"listInfos\">";

        /*
         * Management of the numbers "start" and "end" to display depending on the maxperpage set in the selector
         * These numbers are more user-friendly and do not begin with 0
         */
        echo $this->name." <strong>".min($this->startreal + 1, $count) . "</strong>\n ";
        echo _("to")." <strong>".min($this->endreal + 1, $count)."</strong>\n";

        printf (_(" - Total <b>%s </b>")."\n", $count);
        /* Display page counter only when useful */
        if ($count > $this->maxperpage) {
            echo "("._("page")." ";
            printf("%.0f", ($this->endreal + 1) / $this->maxperpage);
            echo " / ";
            $pages = intval(($count / $this->maxperpage)) ;
            if (($count % $this->maxperpage > 0) && ($count > $this->maxperpage))
                $pages++;
            else if (($count > 0) && ($pages < 1))
                $pages = 1;
            else if ($pages < 0)
                $pages = 0;
            printf("%.0f", $pages);
            echo ")\n";
        }
        echo "</p>";
    }
}

/**
 * specific class for UserDisplay
 */
class UserInfos extends OptimizedListInfos {
    var $css = array(); //css for first column

    function drawMainAction($idx) {
        echo "<td class=\"".$this->css[$idx]."\">";
        echo $this->arrAction[0]->encapsulate($this->arrInfo[$idx], $this->paramInfo[$idx]);
        echo "</td>";
    }

}


/**
 *
 *  Display a previous/next navigation bar for ListInfos widget
 *
 */
class SimpleNavBar extends HtmlElement {

    /**
     * @param $curstart: the first item index to display
     * @param $curent: the last item index
     * @param $itemcount: total number of item
     * @param $filter: the current list filter
     * @param $max: max quantity of elements in a page
     * @param $paginator: boolean which enable the selector of the number of results in a page
     */
    function SimpleNavBar($curstart, $curend, $itemcount, $extra = "", $max = "", $paginator = false) {
        global $conf;
        if(isset($max) && $max != "") {
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

    function display($arrParam = array()) {
        echo '<form method="post">';
        echo "<ul class=\"navList\">\n";

        if ($this->curstart != 0 || ($this->curstart - $this->max > 0)) {
            $start = $this->curstart - $this->max;
            $end = $this->curstart - 1;
            echo "<li class=\"previousList\"><a href=\"".$_SERVER["SCRIPT_NAME"];
            /* FIXME: maybe we can get rid of $_GET["filter"] ? */
            printf("?module=%s&amp;submod=%s&amp;action=%s&amp;start=%d&amp;end=%d&amp;filter=%s%s", $_GET["module"],$_GET["submod"],$_GET["action"],$start, $end, $_GET["filter"], $this->extra);
            echo "\">"._("Previous")."</a></li>\n";
        }

        if($this->paginator) {
            // Display the maxperpage selector
            $this->displaySelectMax();
        }

        if (($this->curend + 1) < $this->itemcount) {
            $start = $this->curend + 1;
            $end = $this->curend + $this->max;
            $filter = isset($_GET["filter"]) ? $_GET["filter"] : "";
            echo "<li class=\"nextList\"><a href=\"".$_SERVER["SCRIPT_NAME"];
            printf("?module=%s&amp;submod=%s&amp;action=%s&amp;start=%d&amp;end=%d&amp;filter=%s%s", $_GET["module"],$_GET["submod"],$_GET["action"],$start, $end, $filter, $this->extra);
            echo "\">"._("Next")."</a></li>\n";
        }

        if($this->paginator) {
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
    function displaySelectMax($jsfunc=null) {
        global $conf;
        echo '<span class="pagination">'._('Pagination').': ';
        if(isset($jsfunc)) {
            $start = $this->curstart;

            echo "<select id=\"maxperpage\" name=\"maxperpage\" onChange=\"updateMaxPerPage(this); return false;\">";
        } else {
            echo "<select id=\"maxperpage\" name=\"maxperpage\">";
        }
        /* Display the selector and each option of the array set in the config
           file */
        foreach($conf["global"]["pagination"] as $quantity) {
            $selected = '';
            if ($_REQUEST['maxperpage'] == $quantity)
                /* Set by default if already selected before */
                $selected = ' selected="selected"';
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
        <script type="javascript">
	    updateMaxPerPage = function(elem) {
            // Get the selector element (the first of the page)
	        var maxperpageElement = document.getElementById('maxperpage');
            if(maxperpageElement != undefined) {
                // Synchronize the value of the two selectors of the page :
                // the ListInfos widget print two Navbar, so the maxperpage value can be changed in both
                maxperpageElement.selectedIndex = elem.selectedIndex;
                var maxperpageValue = elem.value;
                // Evaluate the end depending on the maxperpage value selected
                var end = parseInt(maxperpageValue) + parseInt(<?php echo $start ?>) - 1;
                // Call the function to update the ListInfos
                <?php echo $jsfunc ?>('<?php echo $this->filter ?>', '<?php echo $start ?>', end);
            }
            return false;
        }
        </script>
<?

    }

    /**
     * This function just print a script which add a border at the left of the "Next" link
     */
    function displayNextListBorder() {
?>
        <script type="javascript">
        var nextList = [];
        var nextListClass = "";
        if(document.getElementsByClassName("nextListInactive").length > 0) {
            nextListClass = "nextListInactive";
        }
        if(document.getElementsByClassName("nextList").length > 0) {
            nextListClass = "nextList";
        }
        if(nextListClass != "") {
            nextList = document.getElementsByClassName(nextListClass);
            nextList[0].style.borderLeft = "solid 1px #CCC";
            nextList[1].style.borderLeft = "solid 1px #CCC";
        }
        </script>
<?
    }

    function displayGotoPageField() {
        echo '<script type="text/javascript">
            gotoPage = function(input) {
                page = input.value;
                if (page <= '.$this->nbpages.') {
                    end = ('.$this->max.' * page);
                    start = end - '.$this->max.';
                    end -= 1;
                    cur =  ('.$this->curend.' + 1) / 10;
                    '.$this->jsfunc.'("'.$this->filter.'", start, end, document.getElementById("maxperpage"));
                }
            }
        </script>';
        echo '<span class="pagination">'._("Go to page").': <input type="text" size="2" onchange="gotoPage(this)" /></span>';
    }

    function displayPagesNumbers() {
        # pages links
        # show all pages
        if ($this->nbpages <= 10) {
            if($this->nbpages > 1) {
                echo '<span class="pagination">';
                for($i=1; $i<=$this->nbpages; $i++) {
                    echo $this->makePageLink($i);
                }
                echo '</span>';
            }
        }
        # show start/end pages and current page
        else {
            echo '<span class="pagination">';
            for($i=1; $i<=3; $i++) {
                echo $this->makePageLink($i);
            }
            if($this->curpage > 2 and $this->curpage < 5) {
                for($i=$this->curpage;$i<=$this->curpage+2;$i++) {
                    if ($i > 3)
                        echo $this->makePageLink($i);
                }
            }
            else if ($this->curpage > 4 and $this->curpage < $this->nbpages-3) {
                echo '.. ';
                for($i=$this->curpage-1;$i<=$this->curpage+1;$i++) {
                    echo $this->makePageLink($i);
                }
            }
            echo '.. ';
            if ($this->curpage <= $this->nbpages-2 and $this->curpage >= $this->nbpages-3) {
                for($i=$this->nbpages-4; $i<=$this->nbpages-3; $i++) {
                    echo $this->makePageLink($i);
                }
            }
            for($i=$this->nbpages-2; $i<=$this->nbpages; $i++) {
                echo $this->makePageLink($i);
            }
            echo '</span>';
        }
    }

    function makePageLink($page) {
        $end = ($this->max * $page);
        $start = $end - $this->max;
        $end -= 1;
        if ($page == $this->curpage) {
            return '<span>'.$page.'</span> ';
        }
        else {
            return '<a href="#" onclick="'.$this->jsfunc.'(\''.$this->filter.'\',\''.$start.'\',\''.$end.'\', document.getElementById(\'maxperpage\')); return false;">'.$page.'</a> ';
        }
    }

}

/**
 * Class which creates a SimpleNavBar with the paginator always enabled by
 * default
 */
class SimplePaginator extends SimpleNavBar {

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
    function SimplePaginator($curstart, $curend, $itemcount, $extra = "", $max = "") {
        $this->SimpleNavBar($curstart, $curend, $itemcount, $extra, $max, true);
    }

}

/**
 *  Display a previous/next navigation bar for ListInfos widget
 *  The AjaxNavBar is useful when an Ajax Filter is set for a ListInfos widget
 */
class AjaxNavBar extends SimpleNavBar {

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
    function AjaxNavBar($itemcount, $filter, $jsfunc = "updateSearchParam", $max = "", $paginator = false) {
        global $conf;

        if (isset($_GET["start"])) {
            $curstart = $_GET["start"];
            $curend = $_GET["end"];
        } else {
            $curstart = 0;
            if ($itemcount > 0){
                if($max != "") {
                    $curend = $max -1;
                } else {
                    $curend = $conf["global"]["maxperpage"] - 1;
                }
            } else
                $curend = 0;
        }
        $this->SimpleNavBar($curstart, $curend, $itemcount, null, $max, $paginator);
        $this->filter = $filter;
        $this->jsfunc = $jsfunc;
    }

    function display($arrParam = array()) {
        echo '<form method="post">';
        echo "<ul class=\"navList\">\n";

        if($this->paginator) {
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
class AjaxPaginator extends AjaxNavBar {
    /**
     * Just call the constructor of AjaxNavBar with "true" value for the $paginator attribute
     *
     * @param $itemcount: total number of item
     * @param $filter: the current list filter
     * @param $jsfunc: the name of the javascript function that applies the AJAX filter for the ListInfos widget
     * @param $max: the max number of elements to display in a page
     */
    function AjaxPaginator($itemcount, $filter, $jsfunc = "updateSearchParam", $max = "") {
        $this->AjaxNavBar($itemcount, $filter, $jsfunc, $max, true);
    }

}

/**
 *
 * Create an AjaxFilter Form that updates a div according to an url output
 *
 */

class AjaxFilter extends HtmlElement {

    /**
     * @param $url: URL called by the javascript updated. The URL gets the filter in $_GET["filter"]
     * @param $divid: div ID which is updated by the URL output
     * @param $formid: change the form id (usefull for multiple Ajaxfilter in one page)
     */
    function AjaxFilter($url, $divid = "container", $params = array(), $formid = "") {
        if (strpos($url, "?") === False)
            /* Add extra ? needed to build the URL */
            $this->url = $url . "?";
        else
            /* Add extra & needed to build the URL */
            $this->url = $url . "&";
        $this->divid = $divid;
        $this->formid = $formid;
        $this->refresh= 0;
        $this->params = '';
        foreach ($params as $k => $v) {
            $this->params .= "&".$k."=".$v;
        }

        // get the current module pages
        if (isset($_GET["module"]))
            $__module = $_GET["module"];
        else
            $__module = "default";
        if (isset($_GET["submod"]))
            $__submod = $_GET["submod"];
        else
            $__submod = "default";
        if (isset($_GET["action"]))
            $__action = $_GET["action"];
        else
            $__action = "default";
        if (isset($_GET['tab']))
            $__tab = $_GET['tab'];
        else
            $__tab = "default";
        $extra = "";
        foreach($_GET as $key => $value) {
            if (!in_array($key, array('module', 'submod', 'tab', 'action', 'filter', 'start', 'end', 'maxperpage')))
                $extra += $key + "_" + $value;
        }
        // then get our filter info
        if(isset($_SESSION[$__module."_".$__submod."_".$__action."_".$__tab."_filter_".$extra])) {
            $this->storedfilter = $_SESSION[$__module."_".$__submod."_".$__action."_".$__tab."_filter_".$extra];
        }
        if(isset($_SESSION[$__module."_".$__submod."_".$__action."_".$__tab."_maxperpage_".$extra])) {
            $this->storedmax = $_SESSION[$__module."_".$__submod."_".$__action."_".$__tab."_maxperpage_".$extra];
        }
        if(isset($_SESSION[$__module."_".$__submod."_".$__action."_".$__tab."_start_".$extra])) {
            $this->storedstart = $_SESSION[$__module."_".$__submod."_".$__action."_".$__tab."_start_".$extra];
        }
        if(isset($_SESSION[$__module."_".$__submod."_".$__action."_".$__tab."_end_".$extra])) {
            $this->storedend = $_SESSION[$__module."_".$__submod."_".$__action."_".$__tab."_end_".$extra];
        }
    }

    /**
     * Allow the list to refresh
     * @param $refresh: time in ms
     */
    function setRefresh($refresh) {
        $this->refresh = $refresh;
    }

    function display($arrParam = array()) {
        global $conf;
        $root = $conf["global"]["root"];
        $maxperpage = $conf["global"]["maxperpage"];

?>
<form name="Form<?php echo $this->formid ?>" id="Form<?php echo $this->formid ?>" action="#" onsubmit="return false;">

    <div id="loader<?php echo $this->formid ?>">
        <img id="loadimg" src="<?php echo $root; ?>img/common/loader.gif" alt="loader" class="loader"/>
    </div>
    <div id="searchSpan<?php echo $this->formid ?>" class="searchbox" style="float: right;">
    <img src="graph/search.gif" style="position:relative; top: 5px; float: left;" alt="search" /> <span class="searchfield"><input type="text" class="searchfieldreal" name="param" id="param<?php echo $this->formid ?>" onkeyup="pushSearch<?php echo $this->formid ?>(); return false;" />
    <img src="graph/croix.gif" alt="suppression" style="position:relative; top : 4px;"
    onclick="document.getElementById('param<?php echo $this->formid ?>').value =''; pushSearch<?php echo $this->formid ?>(); return false;" />
    </span>
    </div>

    <script type="text/javascript">
<?
if(!$this->formid) {
?>
        document.getElementById('param<?php echo $this->formid ?>').focus();
<?
}
if(isset($this->storedfilter)) {
?>
        document.Form<?php echo $this->formid ?>.param.value = "<?php echo $this->storedfilter ?>";
<?
}
?>
        var refreshtimer<?php echo $this->formid ?> = null;
        var refreshparamtimer<?php echo $this->formid ?> = null;
        var refreshdelay<?php echo $this->formid ?> = <?php echo  $this->refresh ?>;
        var maxperpage = <?php echo $maxperpage ?>;
<?
if (isset($this->storedmax)) {
?>
        maxperpage = <?php echo $this->storedmax ?>;
<?
}
?>
        if(document.getElementById('maxperpage') != undefined)
            maxperpage = document.getElementById('maxperpage').value;

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
        $url = $this->url."filter='+document.Form".$this->formid.".param.value+'&maxperpage='+maxperpage+'".$this->params;
        if (isset($this->storedstart) && isset($this->storedend)) {
            $url .= "&start=".$this->storedstart."&end=".$this->storedend;
        }
        ?>

        updateSearch<?php echo $this->formid ?> = function() {
            new Ajax.Updater('<?php echo  $this->divid; ?>',
            '<?php echo $url ?>',
            { asynchronous:true, evalScripts: true}
            );

<?
if ($this->refresh) {
?>
            refreshtimer<?php echo $this->formid ?> = setTimeout("updateSearch<?php echo $this->formid ?>()", refreshdelay<?php echo $this->formid ?>)
<?
}
?>
        }

        /**
         * Update div when clicking previous / next
         */
        updateSearchParam<?php echo $this->formid ?> = function(filter, start, end, max) {
            clearTimers<?php echo $this->formid ?>();
            if(document.getElementById('maxperpage') != undefined)
                maxperpage = document.getElementById('maxperpage').value;

            new Ajax.Updater('<?php echo  $this->divid; ?>','<?php echo  $this->url; ?>filter='+filter+'&start='+start+'&end='+end+'&maxperpage='+maxperpage+'<?php echo  $this->params ?>', { asynchronous:true, evalScripts: true});
<?
if ($this->refresh) {
?>
            refreshparamtimer<?php echo $this->formid ?> = setTimeout("updateSearchParam<?php echo $this->formid ?>('"+filter+"',"+start+","+end+","+maxperpage+")", refreshdelay<?php echo $this->formid ?>);
<?
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
<?
          }

    function displayDivToUpdate() {
        print '<div id="' . $this->divid . '"></div>' . "\n";
    }
}

class NoLocationTpl extends AbstractTpl {

    function NoLocationTpl($name) {
        $this->name = $name;
        $this->size = '13';
    }

    function display($arrParam = array()) {
        print '<span class="error">' . _("No item available") . '</span>';
        print '<input name="'.$this->name.'" id="'.$this->name.'" type="HIDDEN" size="'.$this->size.'" value="" class="searchfieldreal" />';
    }

    function setSelected($elemnt) {
    }
}

class SingleLocationTpl extends AbstractTpl {

    function SingleLocationTpl($name, $label) {
        $this->name = $name;
        $this->label = $label;
        $this->value = null;
    }

    function setElementsVal($value) {
        $this->value = array_values($value);
        $this->value = $this->value[0];
    }

    function setSelected($elemnt) {
    }

    function display($arrParam = array()) {
        print $this->label;
        print '<input name="'.$this->name.'" id="'.$this->name.'" type="HIDDEN" value="'. $this->value .'" class="searchfieldreal" />';
    }

}

class AjaxFilterLocation extends AjaxFilter {
    function AjaxFilterLocation($url, $divid = "container", $paramname = 'location', $params = array()) {
        $this->AjaxFilter($url, $divid, $params);
        $this->location = new SelectItem($paramname, 'pushSearch', 'searchfieldreal noborder');
        $this->paramname = $paramname;
    }

    function setElements($elt) {
        if (count($elt) == 0) {
            $this->location = new NoLocationTpl($this->paramname);
        } else if (count($elt) == 1) {
            $loc = array_values($elt);
            $this->location = new SingleLocationTpl($this->paramname, $loc[0]);
        } else {
            $this->location->setElements($elt);
        }
    }

    function setElementsVal($elt) {
        if (count($elt) >= 1) {
            $this->location->setElementsVal($elt);
        }
    }

    function setSelected($elemnt) {
        $this->location->setSelected($elemnt);
    }

    function display($arrParam = array()) {
        global $conf;
        $root = $conf["global"]["root"];
?>
<form name="Form" id="Form" action="#" onsubmit="return false;">
    <div id="loader"><img id="loadimg" src="<?php echo $root; ?>img/common/loader.gif" alt="loader" class="loader"/></div>
    <div id="searchSpan" class="searchbox" style="float: right;">
    <img src="graph/search.gif" style="position:relative; top: 2px; float: left;" alt="search" />
    <span class="searchfield">
<?php
     $this->location->display();
?>
    </span>&nbsp;
    <span class="searchfield"><input type="text" class="searchfieldreal" name="param" id="param" onkeyup="pushSearch(); return false;" />
    <img src="graph/croix.gif" alt="suppression" style="position:relative; top : 3px;"
    onclick="document.getElementById('param').value =''; pushSearch(); return false;" />
    </span>
    </div>

    <script type="text/javascript">
        document.getElementById('param').focus();

<?
if(isset($this->storedfilter)) {
?>
        document.Form.param.value = "<?php echo $this->storedfilter ?>";
<?
}
?>
        var maxperpage = <?php echo $conf["global"]["maxperpage"] ?>;
        if(document.getElementById('maxperpage') != undefined)
            maxperpage = document.getElementById('maxperpage').value;

        /**
        * update div with user
        */
        function updateSearch() {
            launch--;

                if (launch==0) {
                    new Ajax.Updater('<?php echo  $this->divid; ?>','<?php echo  $this->url; ?>filter='+document.Form.param.value+'<?php echo  $this->params ?>&<?php echo  $this->paramname ?>='+document.Form.<?php echo  $this->paramname ?>.value+'&maxperpage='+maxperpage, { asynchronous:true, evalScripts: true});
                }
            }

        /**
        * provide navigation in ajax for user
        */

        function updateSearchParam(filt, start, end) {
            var reg = new RegExp("##", "g");
            var tableau = filt.split(reg);
            var location = "";
            var filter = "";
            var reg1 = new RegExp(tableau[0]+"##", "g");
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
            if(document.getElementById('maxperpage') != undefined)
            {
                maxperpage = document.getElementById('maxperpage').value;
            }

            new Ajax.Updater('<?php echo  $this->divid; ?>','<?php echo  $this->url; ?>filter='+filter+'<?php echo  $this->params ?>&<?php echo  $this->paramname ?>='+location+'&start='+start+'&end='+end+'&maxperpage='+maxperpage, { asynchronous:true, evalScripts: true});
            }

        /**
        * wait 500ms and update search
        */

        function pushSearch() {
            launch++;
            setTimeout("updateSearch()",500);
        }

        pushSearch();
    </script>

</form>
<?
          }
}

class AjaxLocation extends AjaxFilterLocation {

    function AjaxLocation($url, $divid = "container", $paramname = 'location', $params = array()) {
        $this->AjaxFilterLocation($url, $divid, $paramname, $params);
        $this->location = new SelectItem($paramname, 'pushSearchLocation', 'searchfieldreal noborder');
    }

    function display($arrParam = array()) {
        global $conf;
        $root = $conf["global"]["root"];
?>
<form name="FormLocation" id="FormLocation" action="#">
    <div id="Location">
        <span id="searchSpan" class="searchbox">
            <img src="graph/search.gif"/>
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
            launch--;
            if (launch==0) {
                new Ajax.Updater('<?php echo  $this->divid; ?>','<?php echo  $this->url; ?><?php echo  $this->params ?>&<?php echo  $this->paramname ?>='+document.FormLocation.<?php echo  $this->paramname ?>.value, { asynchronous:true, evalScripts: true});
                }
        }
        /**
        * wait 500ms and update search
        */

        function pushSearchLocation() {
            launch++;
            setTimeout("updateSearchLocation()",500);
        }
        pushSearchLocation();
    </script>

</form>
<?
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
class SideMenuItem {
    var $text, $module, $submod, $action, $activebg, $inactivebg;
    /**
     *  main constructor
     * @param $text text for the link
     * @param $module module for link
     * @param $submod sub module for link
     * @param $action action param for link /!\ use for class id too
     * @param $activebg background image to use when menu is currently activated
     * @param $inactivebg background image to use when menu is currently inactivated
     */
    function SideMenuItem($text,$module,$submod,$action, $activebg = "", $inactivebg = "") {
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
    function getLink() {
        return 'main.php?module='.$this->module.'&amp;submod='.$this->submod.'&amp;action='.$this->action;
    }


    /**
     *  display the SideMenuItem on the screen
     */
    function display() {
        if (hasCorrectAcl($this->module, $this->submod, $this->action)) {
            echo '<li id="'.$this->cssId.'">';
            echo '<a href="'.$this->getLink().'">'.$this->text.'</a></li>'."\n";
        }
    }

    /**
     * Allows to set another CSS id then the default one which is the action
     * string
     *
     * @param id: the CSS id to use
     */
    function setCssId($id) {
        $this->cssId = $id;
    }

    /**
     * Return the menu item CSS
     *
     * @param active: this menu item is active
     */
    function getCss($active = False) {
        $bgi_active = $bgi_inactive = "";
        if ($this->activebg != "" && $this->inactivebg != "") {
            $bgi_active = "background-image: url(" . $this->activebg . ");";
            $bgi_inactive = "background-image: url(" . $this->inactivebg . ");";
        }

        if ($active) {
            return "#sidebar ul.$this->submod li#$this->cssId a {
                        background-color: #f6f6f6;
                        color: #444;
                        border-bottom: solid 1px #ccc;
                        border-top: solid 1px #ccc;
                        $bgi_active
            }";
        }
        else if ($bgi_inactive){
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

class SideMenuItemNoAclCheck extends SideMenuItem {
    /**
     *  display the SideMenuItem on the screen
     */
    function display() {
        echo '<li id="'.$this->cssId.'">';
        echo '<a href="'.$this->getLink().'" target="_self">'.$this->text.'</a></li>'."\n";
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
class SideMenu {
    var $itemArray;
    var $className;
    var $backgroundImage;
    var $activatedItem;

    /**
     *  SideMenu default constructor
     *     initalize empty itemArray for SideMenuItem
     */
    function SideMenu() {
        $this->itemArray = array();
        $this->backgroundImage = null;
        $this->activatedItem = null;
    }

    /**
     *  add a sideMenu Item into the SideMenu
     * @param $objSideMenuItem object SideMenuItem
     */
    function addSideMenuItem($objSideMenuItem) {
        $this->itemArray[]=&$objSideMenuItem;
    }

    /**
     * CSS class
     */
    function setClass($class) {
        $this->className=$class;
    }

    /**
     * @return className for CSS
     */
    function getClass() {
        return $this->className;
    }

    /**
     * Set the sidemenu background image
     */
    function setBackgroundImage($bg) {
        $this->backgroundImage = $bg;
    }

    /**
     * Get the sidemenu background image
     */
    function getBackgroundImage() {
        return $this->backgroundImage;
    }

    /**
     *  print the SideMenu and the sideMenuItem
     */
    function display() {
        echo "<style>#section { margin-left: 200px; border-left: 2px solid #bbb; }</style>";
        echo "<div id=\"sidebar\">\n";
        echo "<ul class=\"".$this->className."\">\n";
        foreach ($this->itemArray as $objSideMenuItem) {
            $objSideMenuItem->display();
        }
        echo "</ul>\n";
        echo "</div>\n";
    }

    /**
     *  @return return the Css content for a sidebar
     *  static method to get SideBarCss String
     */
    function getSideBarCss() {
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
    function forceActiveItem($item) {
        $this->activatedItem = $item;
    }

}

/**
 *  PageGenerator class
 */
class PageGenerator {
    var $sidemenu;  /*< SideMenu Object */
    var $content;   /*< array who contains contents Objects */

    /**
     *  Constructor
     */
    function PageGenerator($title = "") {
        $content=array();
        $this->title = $title;
    }

    /**
     *  set the sideMenu object
     */
    function setSideMenu($objSideMenu) {
        $this->sidemenu=$objSideMenu;
    }

    /**
     * Set the page title
     */
    function setTitle($title) {
        $this->title = $title;
    }

    /**
     *  display the whole page
     */
    function display() {
        $this->displaySideMenu();
        if ($this->title)
            $this->displayTitle();
    }

    function displayCss() {
        echo'<style type="text/css">'."\n";
        echo '<!--'."\n";
        echo $this->sidemenu->getSideBarCss();
        echo '-->'."\n";
        echo '</style>'."\n\n";
    }

    /**
     *  display the side Menu
     */
    function displaySideMenu() {
        if ($this->sidemenu) {
            $this->displayCss();
            $this->sidemenu->display();
        }
    }

    /**
     *  display the page title
     */
    function displayTitle() {
        if (isset($this->title)) print "<h2>" . $this->title . "</h2>\n";
    }

    /**
     * Sometimes, we don't want to add the fixheight div in the page
     */
    function setNoFixHeight() {
        $this->fixheight = False;
    }
}

/**
 * Little wrapper that just include a PHP file as a HtmlElement
 */
class DisplayFile extends HtmlElement {

    function DisplayFile($file) {
        $this->HtmlElement();
        $this->file = $file;
    }

    function display($arrParam = array()) {
        require($this->file);
    }
}

/**
 * Class for a tab content
 */
class TabbedPage extends Div {

    function TabbedPage($title, $file) {
        $this->Div(array("class" => "tabdiv"));
        $this->title = $title;
        $this->add(new DisplayFile($file));
    }

    function displayTitle() {
        return "<h2>" . $this->title . "</h2>\n";
    }

    function begin() {
        $s = Div::begin();
        $s .= $this->displayTitle();
        return $s;
    }

}

/**
 * Class for tab displayed by TabSelector
 */
class TabWidget extends HtmlElement {

    function TabWidget($id, $title, $params = array()) {
        $this->id = $id;
        $this->title = $title;
        $this->params = $params;
        $this->active = False;
        $this->last = False;
    }

    function getLink() {
        return urlStr($_GET["module"] . "/" . $_GET["submod"] . "/" . $_GET["action"], array_merge(array("tab" => $this->id), $this->params));
    }

    function setActive($flag) {
        $this->active = $flag;
    }

    function display($arrParam = array()) {
        if ($this->active)
            $klass = ' class="tabactive"';
        else
            $klass = "";
        print '<li id="' . $this->id . '"' . $klass . '"> '
                . '<a href="' . $this->getLink() . '">'
            . $this->title . "</a></li>";
    }

}

/**
 * This class allow to create a page with a tab selector
 */
class TabbedPageGenerator extends PageGenerator {

    function TabbedPageGenerator() {
        $this->PageGenerator();
        $this->topfile = null;
        $this->tabselector = new TabSelector();
        $this->pages = array();
        $this->firstTabActivated = False;
    }

    /**
     * add a header above the tab selector
     */
    function addTop($title, $file) {
        $this->title = $title;
        $this->topfile = $file;
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
    function addTab($id, $tabtitle, $pagetitle, $file, $params = array()) {
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
                        $this->firstTabActivated = True;
                    } else {
                        $this->tabselector->addTab($id, $tabtitle, $params);
                    }
                }
            }
            $this->pages[$id] = array($pagetitle, $file);
        }
    }

    function display() {
        $this->page = null;
        $this->displaySideMenu();
        $this->displayTitle();
        if ($this->topfile) require($this->topfile);
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
        if ($this->page != null) $this->page->display();
    }

}

/**
 * Allow to draw a tab selector
 */
class TabSelector extends HtmlContainer {

    function TabSelector() {
        $this->HtmlContainer();
        $this->tabs = array();
        $this->order = array();
    }

    function getDefaultTab() {
        if (empty($this->elements))
            return null;
        else
            return $this->elements[0];
    }

    function addActiveTab($name, $title, $params = array()) {
        $tab = new TabWidget($name, $title, $params);
        $tab->setActive(True);
        $this->add($tab);
    }

    function addTab($name, $title, $params = array()) {
        $this->add(new TabWidget($name, $title, $params));
    }

    function begin() {
        return '<div class="tabselector"><ul>';
    }

    function end() {
        return "</ul></div>";
    }

}

/**
 * display popup window if notify add in queue
 *
 */
class NotifyWidget {

    /**
     * default constructor
     */
    function NotifyWidget() {
        $this->id = uniqid();
        $this->strings = array();
        // 0: info (default, blue info bubble)
        // 1: error for the moment (red icon)
        // 5 is critical
        $this->level = 0;
        $this->save();
    }

    /**
     * Save the object in the session
     */
    function save() {
        if (!isset($_SESSION["notify"]))
            $_SESSION["notify"] = array();
        if ($this->strings) {
            $_SESSION["notify"][$this->id] = serialize($this);
        }
    }

    function setSize() {
        // Deprecated
        return;
    }

    function setLevel($level) {
        $this->level = $level;
    }

    /**
     * Add a string in notify widget
     * @param $str any HTML CODE
     */
    function add($str) {
        $this->strings[] = $str;
        $this->save();
    }

    function getImgLevel() {
        if ($this->level != 0)
            return "img/common/icn_alert.gif";
        else
            return "img/common/big_icn_info.png";
    }

    function begin() {
        return '<div style="padding: 10px">';
    }

    function content() {
        $str = '<div style="width: 50px; padding-top: 15px; float: left; text-align: center"><img src="' . $this->getImgLevel() . '" /></div><div style="margin-left: 60px">';
        foreach ($this->strings as $string)
            $str .= $string;
        $str .= '</div>';
        return $str;
    }

    function end() {
        $str = '<div style="clear: left; text-align: right; margin-top: 1em;"><button class="btn btn-small" onclick="closePopup()">' . _("Close") . '</button></div></div>';
        return $str;
    }

    function flush() {
        unset($_SESSION["notify_render"][$this->id]);
    }
}

/**
 * display a popup window with a message for a successful operation
 *
 */
class NotifyWidgetSuccess extends NotifyWidget {

    function NotifyWidgetSuccess($message) {
        parent::NotifyWidget();
        $this->add("<div class=\"alert alert-success\">$message</div>");
    }

}

/**
 * display a popup window with a message for a failure
 *
 */
class NotifyWidgetFailure extends NotifyWidget {

    function NotifyWidgetFailure($message) {
        parent::NotifyWidget();
        $this->add("<div class=\"alert alert-error\">$message</div>");
        $this->level = 4;
        $this->save();
    }

}

/**
 * display a popup window with a message for a warning
 *
 */
class NotifyWidgetWarning extends NotifyWidget {

    function NotifyWidgetWarning($message) {
        parent::NotifyWidget();
        $this->add("<div class=\"alert\">$message</div>");
        $this->level = 3;
        $this->save();
    }
}

/**
 * Display a simple DIV with a message
 */
class Message extends HtmlElement {

    function Message($msg, $type = "info") {
        $this->msg = $msg;
        $this->type = $type;
    }

    function display($arrParam = array()) {
        print '<div class="alert alert-' . $this->type . '">' . $this->msg . '</div>';
    }
}

class ErrorMessage extends Message {
    function __construct($msg) {
        parent::__construct($msg, "error");
    }
}
class SuccessMessage extends Message {
    function __construct($msg) {
        parent::__construct($msg, "success");
    }
}
class WarningMessage extends Message {
    function __construct($msg) {
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
function urlStr($link, $param = array(), $ampersandEncode = True) {
    $arr = array();
    $arr = explode ('/',$link);

    if ($ampersandEncode) $amp = "&amp;";
    else $amp = "&";

    $enc_param = "";
    foreach ($param as $key=>$value) {
        $enc_param.= "$amp"."$key=$value";
    }

    if (count($arr) == 3) {
        $ret = "main.php?module=".$arr[0]."$amp"."submod=".$arr[1]."$amp"."action=".$arr[2].$enc_param;
    } else if (count($arr) == 4) {
        $ret = "main.php?module=".$arr[0]."$amp"."submod=".$arr[1]."$amp"."action=".$arr[2]. "$amp" . "tab=" . $arr[3] . $enc_param;
    } else {
        die("Can't build URL");
    }

    return $ret;
}

function urlStrRedirect($link, $param = array()) {
    return(urlStr($link, $param, False));
}

function findInSideBar($sidebar,$query) {
    foreach ($sidebar['content'] as $arr) {
        if (ereg($query,$arr['link'])) {
            return $arr['text'];
        }
    }
}

function findFirstInSideBar($sidebar) {
    return $sidebar['content'][0]['text'];
}


class HtmlElement {

    var $options;

    function HtmlElement() {
        $this->options = array();
    }

    function setOptions($options) {
        $this->options = $options;
    }

    function hasBeenPopped() {
        return True;
    }

    function display($arrParam = array()) {
        die("Must be implemented by the subclass");
    }

}

class HtmlContainer {

    var $elements;
    var $index;
    var $popped;
    var $debug;

    function HtmlContainer() {
        $this->elements = array();
        $this->popped = False;
        $this->index = -1;
    }

    function begin() {
        die("Must be implemented by the subclass");
    }

    function end() {
        die("Must be implemented by the subclass");
    }

    function display() {
        print "\n" . $this->begin() . "\n";
        foreach($this->elements as $element) $element->display();
        print "\n" . $this->end() . "\n";
    }

    function add($element, $options = array()) {
        $element->setOptions($options);
        $this->push($element);
    }

    function push($element) {
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

    function hasBeenPopped() {

        if ($this->popped) $ret = True;
        else if ($this->index == -1) $ret = False;
        else $ret = False;
        return $ret;
    }

    function pop() {
        if (!$this->popped) {
            if ($this->index == -1)
                $this->popped = True;
            else if ($this->elements[$this->index]->hasBeenPopped())
                $this->popped = True;
            else $this->elements[$this->index]->pop();
            //if ($this->popped) print "popping " . $this->options["id"] . "<br>";
        } else die("Nothing more to pop");
    }

}


class Div extends HtmlContainer {

    function Div($options = array(), $class = Null) {
        $this->HtmlContainer();
        $this->name = $class;
        $this->options = $options;
        $this->display = True;
    }

    function begin() {
        $str = "";
        foreach($this->options as $key => $value) $str.= " $key=\"$value\"";
        if (!$this->display) $displayStyle = ' style =" display: none;"';
        else $displayStyle = "";
        return "<div$str$displayStyle>";
    }

    function end () {
        return "</div>";
    }

    function setVisibility($flag) {
        $this->display = $flag;
    }

}

class Form extends HtmlContainer {

    function Form($options = array()) {
        $this->HtmlContainer();
        if (!isset($options["method"]))
            $options["method"] = "post";
        if (!isset($options["id"]))
            $options["id"] = "Form";
        $this->options = $options;
        $this->buttons = array();
        $this->summary = NULL;
    }

    function begin() {
        $str = "";
        foreach($this->options as $key => $value) $str.= " $key=\"$value\"";
        $ret = "<form$str>";
        if (isset($this->summary)) {
            $ret = "<p>" . $this->summary . "</p>\n" . $ret;
        }
        return $ret;
    }

    function end() {
        $str = "";
        foreach($this->buttons as $button) $str .= "\n$button\n";
        $str .= "\n</form>\n";
        return $str;
    }

    function addButton($name, $value, $klass = "btnPrimary", $extra = "", $type = "submit") {
        $b = new Button();
        $this->buttons[] = $b->getButtonString($name, $value, $klass, $extra, $type);
    }

    function addValidateButton($name) {
        $b = new Button();
        $this->buttons[] = $b->getValidateButtonString($name);
    }

    function addCancelButton($name) {
        $b = new Button();
        $this->buttons[] = $b->getCancelButtonString($name);
    }

    function addExpertButton($name, $value) {
        $d = new DivExpertMode();
        $b = new Button();
        $this->buttons[] = $d->begin() . $b->getButtonString($name, $value) . $d->end();
    }

    function addSummary($msg) {
        $this->summary = $msg;
    }

    function getButtonString($name, $value, $klass = "btnPrimary", $extra = "", $type = "submit") {
        $b = new Button();
        return $b->getButtonString($name, $value, $klass, $extra, $type);
    }

    function addOnClickButton($text, $url) {
        $b = new Button();
        $this->buttons[] = $b->getOnClickButton($text, $url);
    }
}

class Button {
    function Button($module = null, $submod = null, $action = null) { # TODO also verify ACL on tabs
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

    function getButtonString($name, $value, $klass = "btnPrimary", $extra = "", $type = "submit") {
        if (hasCorrectAcl($this->module,$this->submod,$this->action)) {
            return $this->getButtonStringWithRight($name, $value, $klass, $extra, $type);
        } else {
            return $this->getButtonStringWithNoRight($name, $value, $klass, $extra, $type);
        }
    }

    function getButtonStringWithRight($name, $value, $klass = "btnPrimary", $extra = "", $type = "submit") {
        return "<input type=\"$type\" name=\"$name\" value=\"$value\" class=\"$klass\" $extra />";
    }
    function getButtonStringWithNoRight($name, $value, $klass = "btnPrimary", $extra = "", $type = "submit") {
        return "<input disabled type=\"$type\" name=\"$name\" value=\"$value\" class=\"btnDisabled\" $extra />";
    }

    function getValidateButtonString($name, $klass = "btnPrimary", $extra = "", $type = "submit") {
        return $this->getButtonString($name, _("Confirm"), $klass);
    }

    function getCancelButtonString($name, $klass = "btnSecondary", $extra = "", $type = "submit") {
        return $this->getButtonString($name, _("Cancel"), $klass);
    }

    function getOnClickButton($text, $url, $klass = "btnPrimary", $extra = "", $type = "button") {
        return $this->getButtonString("onclick", $text, $klass, $extra = "onclick=\"location.href='" . $url . "';\"", $type);
    }
}

class ValidatingForm extends Form {

    function ValidatingForm($options = array()) {
        $this->Form($options);
        $this->options["onsubmit"] = "selectAll('" . $this->options["id"] . "'); return validateForm('" . $this->options["id"]. "');";
    }

    function end() {
        $str = parent::end();
        $str .= "
        <script type=\"text/javascript\">
            if(Form.findFirstElement(\"".$this->options["id"]."\")) {
                Form.focusFirstElement(\"".$this->options["id"]."\");
            }
        </script>\n";
        return $str;
    }

}

/**
 *
 * Allow to easily build the little popup displayed when deleting a user for example
 *
 */
class PopupForm extends Form {

    function PopupForm($title) {
        $options = array("action" => $_SERVER["REQUEST_URI"]);
        $this->Form($options);
        $this->title = $title;
        $this->text = array();
        $this->ask = "";
    }

    function begin() {
        $str = "<h2>" . $this->title . "</h2>\n";
        $str .= parent::begin();
        foreach($this->text as $text)
            $str .= "<p>" . $text . "</p>";
        return $str;
    }

    function end() {
        $str = "<p>" . $this->ask . "</p>";
        $str .= parent::end();
        return $str;
    }

    function addText($msg) {
        $this->text[] = $msg;
    }

    function setQuestion($msg) {
        $this->ask = $ask;
    }

    function addValidateButtonWithFade($name) {
        $this->buttons[] = $this->getButtonString($name, _("Confirm"), "btnPrimary", "onclick=\"new Effect.Fade('popup'); return true;\"" );
    }

    function addCancelButton($name) {
        $this->buttons[] = $this->getButtonString($name, _("Cancel"), "btnSecondary", "onclick=\"new Effect.Fade('popup'); return false;\"" );
    }

}

/**
 *
 * Allow to easily build the little popup, summon a new window
 *
 */
class PopupWindowForm extends PopupForm {

    function PopupWindowForm($title) {
        $options = array("action" => $_SERVER["REQUEST_URI"]);
        $this->PopupForm($options);
        $this->title = $title;
        $this->text = array();
        $this->ask = "";
        $this->target_uri = "";
    }

    function addValidateButtonWithFade($name) {
        $this->buttons[] = $this->getButtonString($name, _("Confirm"), "btnPrimary", "onclick=\"new Effect.Fade('popup'); window.open('".$this->target_uri."', '', 'toolbar=no, location=no, menubar=no, status=no, status=no, scrollbars=no, width=330, height=200'); return false;\"" );
    }
}

class Table extends HtmlContainer {

    function Table($options = array()) {
        $this->HtmlContainer();
        $this->lines = array();
        $this->tr_style = '';
        $this->td_style = '';
        $this->options = $options;
        if (isset($options['tr_style'])) { $this->tr_style = $options['tr_style']; }
        if (isset($options['td_style'])) { $this->td_style = $options['td_style']; }
    }

    function setLines($lines) {
        $this->lines = $lines;
    }

    function begin() {
        return '<table cellspacing="0">';
    }

    function end() {
        return "</table>";
    }

    function getContent() {
        $str = '';
        foreach ($this->lines as $line) {
            $str .= sprintf("<tr%s><td%s>%s</td></tr>", $this->tr_style, $this->td_style, implode(sprintf('</td><td%s>', $this->td_style), $line));
        }
        return $str;
    }

    function displayTable($displayContent = False) {
        print $this->begin();
        if ($displayContent) {
            print $this->getContent();
        }
        print $this->end();
    }

}

class DivForModule extends Div {

    function DivForModule($title, $color, $options = array()) {
        $options["style"] = "background-color: " . $color;
        $options["class"] = "formblock";
        $this->Div($options);
        $this->title = $title;
        $this->color = $color;
    }

    function begin() {
        print parent::begin();
        print "<h3>" . $this->title . "</h3>";
    }
}

class DivExpertMode extends Div {

    function begin() {
        $str = '<div id="expertMode" ';
        if (isExpertMode()) {
            $str .= ' style="display: inline;"';
        } else {
            $str .= ' style="display: none;"';
        }
        return $str . ' >';
    }

}

class ModuleTitleElement extends HtmlElement{

    function ModuleTitleElement($title){
        $this->title=$title;
    }

    function display($arrParam = array()){
        print '<br><h1>'.$this->title.'</h1>';
    }
}

class TitleElement extends HtmlElement {
    function TitleElement($title, $level = 2){
        $this->title=$title;
        $this->level = $level;
    }
    function display($arrParam = array()){
        print '<br/><h'.$this->level.'>'.$this->title.'</h'.$this->level.'>';
    }
}

class SpanElement extends HtmlElement {
    function SpanElement($content, $class = Null){
        $this->name = $class;
        $this->content = $content;
        $this->class = $class;
    }

    function display($arrParam = array()){
        if ($this->class) {
            $class = ' class="' . $this->class . '"';
        }
        else {
            $class = '';
        }
        printf ('<span%s>%s</span>', $class, $this->content);
    }
}

class SelectElement extends HtmlElement{

    function SelectElement($name, $nametab){
        $this->name = $name;
        $this->nametab = $nametab;
    }

    function display($arrParam = array()) {
        print '<a href="javascript:void(0);" onclick="checkAll(\''.$this->name.'\',1);checkAll(\''.$this->nametab.'\',1);">'._("Select all").' </a> / ';
        print '<a href="javascript:void(0);" onclick="checkAll(\''.$this->name.'\',0);checkAll(\''.$this->nametab.'\',0);">'._("Unselect all").'</a><br/>';
    }
}

class TrTitleElement extends HtmlElement{

        function TrTitleElement($arrtitles){
            $this->titles=$arrtitles;
        }

        function display($arrParam = array()){
            $colsize=100/sizeof($this->titles);
            print '<tr>';
            foreach( $this->titles as $value ){
                    print '<td width="'.$colsize.'%"><b>'.$value.'</b></td>';
            }
            print '</tr>';
        }
}

class AjaxPage extends HtmlElement {

    function AjaxPage($url, $id = "container", $params = array(), $refresh = 10) {
        $this->url = $url;
        $this->id = $id;
        $this->class = "";
        $this->params = json_encode($params);
        $this->refresh = $refresh;
    }

    function display($arrParam = array()) {
echo <<< EOT
        <div id="{$this->id}" class="{$this->class}"></div>
        <script type="text/javascript">
        new Ajax.PeriodicalUpdater("{$this->id}", "{$this->url}", {
            method: "get",
            frequency: {$this->refresh},
            parameters: {$this->params},
            evalScripts: true
        });
        </script>
EOT;
    }
}

?>

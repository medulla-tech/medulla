<?php

class DisabledInputTpl extends AbstractTpl{
    /**
     *  display input Element
     *  $arrParam accept ["value"] to corresponding value
     */
    function display($arrParam = array()) {
        if ($arrParam=='') {
            $arrParam = $_POST[$this->name];
        }

        $required_attr = isset($arrParam["required"])?' rel="required"':'';
        $regexp_attr = isset($this->regexp)?' regexp="'.$this->regexp.'"':'';

        print '<span id="container_input_'.$this->name.'"><input name="'.$this->name.'" id="'.$this->name.'" type="" value="'.$arrParam["value"].'" disabled="'.$arrParam["disabled"].$required_attr.$regexp_attr.'" /></span>';

        if (isset($arrParam["onchange"])) {
            print '<script type="text/javascript">';
            print 'jQuery(\'#'.$this->name.'\').change( function() {' . $arrParam["onchange"] . '});';
            print '</script">';
        }
    }
}

class LinkTrFormElement extends TrFormElement{

        function display($arrParam = array()) {

            if (empty($arrParam)) $arrParam = $this->options;

            if (!isset($this->cssErrorName)) $this->cssErrorName = $this->template->name;

            print '<tr><td width="40%" ';
            print displayErrorCss($this->cssErrorName);
            print 'style = "text-align: right;">';

            //if we got a tooltip, we show it
            if ($this->tooltip) {
                print "<a href=\"#\" class=\"tooltip\">".$this->desc."<span>".$this->tooltip."</span></a>";
            } else {
                print $this->desc;
            }
            print '</td><td>';
            print "<a href=\"".$arrParam["value"]."\">".$arrParam["name"];
            print "</a>";
            if (isset($arrParam["extra"])) {
                print "&nbsp;" . $arrParam["extra"];
            }
            print "</td></tr>";

        }
}

class AjaxLogNavBar extends SimpleNavBar {

    /**
     *
     * The AjaxNavBar start/end item are get from $_GET["start"] and $_GET["end"]
     *
     * @param $itemcount: total number of item
     * @param $filter: the current list filter
     * @param $extra: extra URL parameter to pass the next/list button
     * @param $jsfunc: the name of the javascript function that applies the AJAX filter for the ListInfos widget
     */
    function __construct($itemcount, $filter, $maxperpage, $jsfunc = "updateSearchParam",$extra="" ) {
        global $conf;
        $this->itemcount = $itemcount;
        $this->extra = $extra;
        $this->max = $maxperpage;
        if (isset($_GET["start"])) {
            $this->curstart = $_GET["start"];
            $this->curend = $_GET["end"];
        } else {
            $this->curstart = 0;
            if ($this->itemcount > 0)
                $this->curend = $this->max - 1;
            else
                $this->curend = 0;
        }
        parent::__construct($this->curstart, $this->curend, $this->itemcount, null, $this->max);
        $this->filter = $filter;
        $this->jsfunc = $jsfunc;
    }

    function display($arrParam = array()) {
        echo '<form method="post">';
        echo "<ul class=\"navList\">\n";

        // show goto page field
        if ($this->nbpages > 20) {
            $this->displayGotoPageField();
        }

        if ($this->curstart == 0)
            echo "<li class=\"previousListInactive\">" . _("Previous") . "</li>\n";
        else {
            $start = $this->curstart - $this->max;
            $end = $this->curstart - 1;
            echo "<li class=\"previousList\"><a href=\"#\" onClick=\"" . $this->jsfunc . "('" . $this->filter . "','$start','$end'); return false;\">" . _("Previous") . "</a></li>\n";
        }

        // display pages numbers
        $this->displayPagesNumbers();

        if (($this->curend + 1) >= $this->itemcount)
            echo "<li class=\"nextListInactive\">"._("Next")."</li>\n";
        else {
            $start = $this->curend + 1;
            $end = $this->curend + $this->max;
            echo "<li class=\"nextList\"><a href=\"#\" onClick=\"" . $this->jsfunc . "('" . $this->filter . "','$start','$end'); return false;\">" . _("Next") . "</a></li>\n";
        }

        // Display a border at the left of the "Next" link
        if ($this->nbpages > 1) {
            $this->displayNextListBorder();
        }

        echo "</ul>\n";
    }

}

/**
 * date input template
 */
class LogDynamicDateTpl extends InputTpl {

    function __construct($name,$defaultvalue) {
        $this->name = $name;
        $this->value = $defaultvalue;
    }

    function display($arrParam = array()) {
        $e = new InputTpl($this->name);
        if (!isset($GLOBALS["__JSCALENDAR_SOURCED__"])) { // to avoid double-sourcing
            $GLOBALS["__JSCALENDAR_SOURCED__"] = 1;
            print '
            <script type="text/javascript" src="graph/jscalendar/js/calendar_stripped.js" charset="utf-8"></script>
            <script type="text/javascript" src="graph/jscalendar/js/calendar-setup_stripped.js" charset="utf-8"></script>
            <style type="text/css">@import url("graph/jscalendar/css/calendar-blue.css");</style>
            <script type="text/javascript" src="graph/jscalendar/lang/calendar-en.js" charset="utf-8"></script>
            <script type="text/javascript">
                function ValidDates(){
                    pushSearch();
                }
            </script>
            ';
            if (isset($_REQUEST["lang"])) { // EN calendar always read, as the next one may not exists
                $extention = substr($_REQUEST["lang"], 0, 2); // transpose LANG, f.ex. fr_FR => fr
                print '<script type="text/javascript" src="graph/jscalendar/lang/calendar-'.$extention.'.js" charset="utf-8"></script>';
            }
        }

        print '
            <span id="container_input_'.$this->name.'">
                <input name="'.$this->name.'" id="'.$this->name.'" type="text" size="'.$this->size.'" value="'.$this->value.'" readonly="1" onChange="ValidDates();"/>
                <input
                    type="image"
                    style="vertical-align: bottom;"
                    src="graph/jscalendar/img/calendar.png"
                    id="'.$this->name.'_button"
                />
        ';

        // ugly gettext workaround
        if (isset($arrParam["ask_for_now"])) {
            print _("or <a href='#'");
            print " onclick='javascript:document.getElementById(\"".$this->name."\").";
            print _("value=\"now\";'>now</a>");
        } elseif (isset($arrParam["ask_for_never"])) {
            print _("or <a href='#'");
            print " onclick='javascript:document.getElementById(\"".$this->name."\").";
            print _("value=\"never\";'>never</a>");
        }
        print '
            </span>';
        print '
            <script type="text/javascript" charset="utf-8">
            Calendar.setup({ inputField:"'.$this->name.'", ifFormat:"%Y-%m-%d %H:%M:%S", showsTime:true, timeFormat:"24", button:"'.$this->name.'_button", firstDay:1, weekNumbers:false });
            </script>';
    }
}


/**
 * A modified version of Listinfos for Log table
 */
class LogListInfos extends OptimizedListInfos {

    function addCommitInfo($arrString, $description= "") {
        $this->arrCommit = $arrString;
        $this->commit[] = $description;
    }

    function initVar() {
        $this->name="Elements";
        global $conf;
        if (!isset($_GET["start"])) {
            if (!isset($_POST["start"])) {
               $this->start = 0;
               if (count($this->arrInfo) > 0) {
                   $this->end = $conf["global"]["maxperpage"] - 1;
               }
               else {
                   $this->end = 0;
               }
            }
        }
        else {
            $this->start = $_GET["start"];
            $this->end = $_GET["end"];
        }

        $this->maxperpage = $conf["global"]["maxperpage"];
        $this->setItemCount(count($this->arrInfo));
        $this->startreal = $this->start;
        $this->endreal = $this->end;
    }

    function drawTable($navbar = 1) {
        echo "<table border=\"1\" cellspacing=\"0\" cellpadding=\"5\" class=\"listinfos\">\n";
        echo "<thead><tr>";
        foreach ($this->description as $key => $desc) {
            if (isset($this->col_width[$key])) {
                $width_styl = 'width: '.$this->col_width[$key].';';
            }
            else {
                $width_styl = '';
            }
            if (!isset($first)) {

                if (!isset($this->first_elt_padding)) {
                    $this->first_elt_padding = 32;
                }
                echo "<td style=\"$width_styl\"><span style=\"color: #777; padding-left: ".$this->first_elt_padding."px;\">$desc</span></td>";
                $first = 1;

            } else {
                echo "<td style=\"$width_styl\"><span style=\"color: #777;\">$desc</span></td>";
            }
        }

        if (count($this->arrAction)!=0) { //if we have actions
            echo "<td style=\"text-align:right;\"><span style=\"color: #AAA;\" >Actions</span></td>";
        }

        echo "</tr></thead>";

        for ($idx = $this->start; ($idx < count($this->arrInfo)) && ($idx <= $this->end); $idx++) {

            if (($this->start - $idx) % 2) {
                echo '<tr class="';
            } else {
                echo '<tr class="alternate ';
            }
            if($this->arrCommit[$idx]==0) {
                echo 'error';
            }
            echo '">';

            //link to first action (if we have an action)
            if (count($this->arrAction) && $this->firstColumnActionLink) {
                $this->drawMainAction($idx);
            } else {
                echo "<td>";
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
}


class AjaxFilterLog extends AjaxFilter {
    function __construct($url, $type, $module="all", $divid = "container" ) {
        parent::__construct($url, $divid);
        $this->begindate = new LogDynamicDateTpl("begindate",_("Begin date"));
        $this->enddate = new LogDynamicDateTpl("enddate",_("End date"));
        $this->filtertype = new SelectItem("filtertype");
        $this->types = $type;
        $this->filtertype->setElements(array_values($type));
        $this->filtertype->setElementsVal(array_keys($type));
        $this->page= $module;
        //$this->filter = new SelectItem("filter");
    }
    function setsearchbar($url){
        $this->urlsearch=$url;
    }

    function display($arrParam = array()){


?>
<form name="Form" id="Form" class="ajaxfilterlog" action="#" onsubmit="return false;">
    <div id="loader"><img id="loadimg" src="img/common/loader.gif" alt="loader" class="loader"/></div>
    <div id="searchSpan" class="searchboxlog">
        <span class="searchfieldfilter">
<?php
        $this->enddate->setSize(15);
        $this->begindate->setSize(15);
        $this->begindate->display(array("update_search"=>True));
        $this->enddate->display(array("update_search"=>True));
        //$this->filtertype->display();
?>
        <span class="searchtools">
            <select name="filtertype" onChange="searchbar()">

<?php

    foreach ($this->types as $key => $item){
        print "\t<option value=\"".$key."\">"._($item)."</option>\n";
    }

?>
            </select>
            <span id="searchfilter">
            </span>
            <img src="img/common/reload.png" style="vertical-align: middle; margin-left: 2px; margin-right: 10px;" onclick="pushSearch(); return false;" title="<?php echo _("Refresh") ?>" />
        </span>
    </span>&nbsp;
    </div>
    <script type="text/javascript">

        jQuery(document).ready(function(){
            searchbar();
        });

        /**
        * update div with user
        */
        function searchbar() {
            jQuery('#searchfilter').load('<?php echo $this->urlsearch ?>&filtertype='+document.Form.filtertype.value,pushSearch);
        }

        function updateSearch() {
            launch--;
            if (launch==0) {
                if (document.getElementById('param') == null)
                    jQuery('#<?php echo  $this->divid; ?>').load('<?php echo  $this->url; ?>filter=&filtertype='+document.Form.filtertype.value+'&begindate='+encodeURI(document.Form.begindate.value)+'&enddate='+document.Form.enddate.value+'&page=<?php echo  $this->page; ?>');
                else
                    jQuery('#<?php echo  $this->divid; ?>').load('<?php echo  $this->url; ?>filter='+encodeURIComponent(document.Form.param.value)+'&filtertype='+document.Form.filtertype.value+'&begindate='+encodeURI(document.Form.begindate.value)+'&enddate='+document.Form.enddate.value+'&page=<?php echo  $this->page; ?>');
            }
        }

        /**
        * provide navigation in ajax for user
        */

        function updateSearchParam(filter, start, end) {
            var reg = new RegExp("##", "g");
            var tableau = filter.split(reg);
            filter = tableau[0];
            var location = tableau[1];
            jQuery('#<?php echo  $this->divid; ?>').load('<?php echo  $this->url; ?>filter='+encodeURIComponent(document.Form.param.value)+'&filtertype='+document.Form.filtertype.value+'&begindate='+encodeURI(document.Form.begindate.value)+'&enddate='+document.Form.enddate.value+'&page=<?php echo  $this->page; ?>&start='+start+'&end='+end);
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
<?php
          }
}

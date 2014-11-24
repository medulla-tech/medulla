<?php


//display the return of api for debug
function expand_arr($array) {
    foreach ($array as $key1) {
        foreach ($key1 as $key => $value) {
            if (is_array($value)) {
                    echo "<i>".$key."</i>:<div style=\"margin-left: 20px;\" >";
                    expand_arr($value);
                    echo "</div>\n";
                } else {
                    echo "<i>".$key."</i>: ".$value."<br>\n";
                }
            }
    }
    echo "<br>\n\n\n";
}

//return  an array in a one string to print it
function get_arr($array) {
    foreach ($array as $key1) {
        foreach ($key1 as $key => $value) {
            if (is_array($value)) {
                    $arg =$arg."<i>".$key."</i>:<div style=\"margin-left: 20px;\" >";
                    $arg = $arg.get_arr($value);
                } else {
                    $arg = $arg."<i>".$key."</i>: ".$value."<br>";
                }
            }
    }
    return $arg;
}

//display the graph with his URL
function zabbixPrintGraph($url, $graphid, $width, $height, $time) {

$p = $url."/chart2.php?graphid=".$graphid."&width=".$width."&height=".$height."&period=".$time;
echo "<img src=".$p.">";
echo "</br></br>";
}

//calcul difference de temps entre 2 timestamp
function diffTime($date1, $date2) {
    $result = array();
    $diff = abs($date1 - $date2);
    $result['abs'] = $diff;
    $tmp = $diff;
    $result['second'] = $tmp % 60;
    $tmp = floor( ($tmp - $result['second']) / 60);
    $result['minute'] = $tmp % 60;
    $tmp = floor( ($tmp - $result['minute']) / 60);
    $result['hour'] = $tmp % 24;
    $tmp = floor( ($tmp - $result['hour']) / 24);
    $result['day'] = $tmp;

    $result2 = array();
    $result2['abs'] = $diff;
    $result2['time'] = $result['day']." Day(s) ".$result['hour']." Hour(s) ".$result['minute']." minute(s) ".$result['second']." second(s)";

    return $result2;
}

class AjaxPrintGraph extends AjaxFilterLocation {

    protected $zabbixUrl;

    function AjaxPrintGraph($url, $divid = "container", $paramname = 'location', $params = array(), $zabbixurl = 'http://localhost/zabbix' ) {
    $this->zabbixUrl = $zabbixurl;
        $this->AjaxFilterLocation($url, $divid, $paramname, $params);
        $this->location = new SelectItem($paramname, 'pushSearchLocationGraph', 'searchfieldreal noborder');
    }

    function display($arrParam = array()) {
        global $conf;
        $root = $conf["global"]["root"];
        ?>

        <form name="FormLocationGraph" id="FormLocationGraph" action="#" onsubmit="return false;">
            <div id="Location">
                <span id="searchSpan" class="searchbox">
                    <img src="graph/search.gif"/>
                    <span class="locationtext">&nbsp;<?php echo _T("Select graph", "monitoring") ?>:&nbsp;</span>
                    <span class="locationfield">
                        <?php
                        $this->location->display();
                        ?>
                    </span>
                </span>
                <img id="loadimg" src="<?php echo $root; ?>img/common/loader.gif" alt="loader" />
            </div>

        <form name="FormLocationPeriod" id="FormLocationPeriod" action="#" onsubmit="return false;">
            <div id="Location">
                <span id="searchSpan" class="searchbox">
                    <img src="graph/search.gif"/>
                    <span class="locationtext">&nbsp;<?php echo _T("Select period", "monitoring") ?>:&nbsp;</span>
                    <span class="locationfield">
                <select id="period" class="searchfieldreal noborder" name="period" onchange="pushSearch(); return false;">
                    <?php
                    $ini_file="/etc/mmc/plugins/monitoring.ini";
                    if (file_exists($ini_file))
                    {
                        $ini=parse_ini_file($ini_file,true);
                        $timeName =$ini["periods"][name];
                        $timeValue = $ini["periods"][duration];
                        $count = count($timeName);

                        // create selection with periods
                        for ($i = 1; $i < $count+1; $i++) {
                            echo "<option value=\"$timeValue[$i]\" >";
                            echo _T($timeName[$i],'monitoring');
                            echo "</option>";
                        }
                    }
                    ?>
                </select>
                    </span>
                </span>
            </div>

            <script type="text/javascript">
                /**
                 * update div with user
                 */


                function updateSearchLocationGraph() {

            var div = document.getElementById('<?php echo $this->divid; ?>');
            var graphId = document.FormLocationGraph.<?php echo $this->paramname; ?>.value;
            var period = document.getElementById("period");
            var test = document.getElementById("graphId");
            if (test != null)
                document.getElementById("graphId").src = "<?php echo $this->zabbixUrl; ?>" + "/chart2.php?graphid=" + graphId +"&period=" + period.value;
            else {
                var image = document.createElement("img");
                image.id = "graphId";
                image.src = "<?php echo $this->zabbixUrl; ?>" + "/chart2.php?graphid=" + graphId +"&period=" + period.value;
                div.appendChild(image);
            }

                }
                /**
                 * wait 500ms and update search
                 */

                function pushSearchLocationGraph() {

                    setTimeout("updateSearchLocationGraph()", 500);
                }

        var graph = document.getElementById("FormLocationGraph");
        graph.onchange = function() {
            pushSearchLocationGraph();
        };

                pushSearchLocationGraph();
            </script>

        </form></form>
        <?php
    }

}

class AjaxFilterLocationFormid extends AjaxFilterLocation {

    function AjaxFilterLocationFormid($url, $divid = "container", $paramname = 'location', $params = array(), $formid = "") {
        $this->AjaxFilter($url, $divid, $params, $formid);
        $this->location = new SelectItem($paramname, 'pushSearch'.$formid, 'searchfieldreal noborder');
        $this->paramname = $paramname;
    $this->formid = $formid;
    }

    function display($arrParam = array()) {
        global $conf;
        $root = $conf["global"]["root"];
        ?>

        <form name="Form<?php echo $this->formid ?>" id="Form<?php echo $this->formid ?>" action="#" onsubmit="return false;">
            <div id="loader"><img id="loadimg" src="<?php echo $root; ?>img/common/loader.gif" alt="loader" class="loader"/></div>
            <div id="searchSpan" class="searchbox" style="float: right;">
                <img src="graph/search.gif" style="position:relative; top: 2px; float: left;" alt="search" />
                <span class="searchfield">
                    <?php
                    $this->location->display();
                    ?>
                </span>&nbsp;
                <span class="searchfield"><input type="text" class="searchfieldreal" name="param" id="param" onkeyup="pushSearch<?php echo $this->formid ?>();
                        return false;" />
                    <img src="graph/croix.gif" alt="suppression" style="position:relative; top : 3px;"
                         onclick="document.getElementById('param').value = '';
                                 pushSearch<?php echo $this->formid ?>();
                                 return false;" />
                </span>
            </div>

            <script type="text/javascript">
                jQuery('#param').focus();
                var refreshtimer = null;
                var refreshparamtimer = null;
                var refreshdelay = <?php echo $this->refresh; ?>;
        <?php
        if (isset($this->storedfilter)) {
            ?>
                    document.Form<?php echo $this->formid ?>.param.value = "<?php echo $this->storedfilter ?>";
            <?php
        }
        ?>
                var maxperpage = <?php echo $conf["global"]["maxperpage"] ?>;
                if (jQuery('#maxperpage').length)
                    maxperpage = jQuery('#maxperpage').val();

                /**
                 * Clear the timers set vith setTimeout
                 */
                function clearTimers<?php echo $this->formid; ?>() {
                    if (refreshtimer != null) {
                        clearTimeout(refreshtimer);
                    }
                    if (refreshparamtimer != null) {
                        clearTimeout(refreshparamtimer);
                    }
                }


                /**
                 * update div with user
                 */


                function updateSearch<?php echo $this->formid ?>() {

                        jQuery.ajax({
                            'url': '<?php echo $this->url; ?>filter=' + encodeURIComponent(document.Form<?php echo $this->formid ?>.param.value) + '<?php echo $this->params ?>&<?php echo $this->paramname ?>=' + document.Form<?php echo $this->formid ?>.<?php echo $this->paramname ?>.value + '&maxperpage=' + maxperpage,
                            type: 'get',
                            success: function(data) {
                                jQuery("#<?php echo $this->divid; ?>").html(data);
                            }
                        });

        <?php
        if ($this->refresh) {
            ?>
                        refreshparamtimer = setTimeout("updateSearch<?php echo $this->formid; ?>()", refreshdelay);
            <?php
        }
        ?>
        }

                /**
                 * provide navigation in ajax for user
                 */

                updateSearchParam = function(filt, start, end) {
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
                        location = document.Form<?php echo $this->formid ?>.<?php echo $this->paramname ?>.value;
                    if (!filter)
                        filter = document.Form<?php echo $this->formid ?>.param.value;

                    jQuery.ajax({
                        'url': '<?php echo $this->url; ?>filter=' + encodeURIComponent(filter) + '<?php echo $this->params ?>&<?php echo $this->paramname ?>=' + location + '&start=' + start + '&end=' + end + '&maxperpage=' + maxperpage,
                        type: 'get',
                        success: function(data) {
                            jQuery("#<?php echo $this->divid; ?>").html(data);
                        }
                    });


        <?php
        if ($this->refresh) {
            ?>
                        refreshparamtimer = setTimeout("updateSearchParam<?php echo $this->formid ?>('" + filter + "'," + start + "," + end + ")", refreshdelay);
            <?php
        }
        ?>
                }

                /**
                 * wait 500ms and update search
                 */

                function pushSearch<?php echo $this->formid ?>() {
                    clearTimers<?php echo $this->formid; ?>();
                    refreshtimer = setTimeout("updateSearch<?php echo $this->formid ?>()", 500);
                }

                pushSearch<?php echo $this->formid ?>();
            </script>

        </form>
        <?php
    }

}

class buttonTpl extends AbstractTpl {
    var $class = '';
    var $cssClass = 'btn btn-small';

    function buttonTpl($id,$text,$class='') {
        $this->id = $id;
        $this->text = $text;
        $this->class = $class;
    }


    function setClass($class) {
        $this->cssClass = $class;
    }

    function display($arrParam) {
        if (isset($this->id,$this->text))
            printf('<input id="%s" type="button" value="%s" class="%s %s" />',$this->id,$this->text,$this->cssClass,$this->class);
    }
}


?>

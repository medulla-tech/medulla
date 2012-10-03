<?php if ($_SESSION['__notify'])  { ?>
<script>
    window.location= 'main.php'
</script>
<?

exit(6);

}
?>
<div style="width:99%">
<?


$connectionNumber = array();
$action = array();
$extra = array();
$date = array();
$oparr = array();

/*
 * FIXME: remove this try and see http://projects.mandriva.org/issues/1867
 */
try {
    foreach (xmlCall("base.getLdapLog",array($_SESSION['ajax']['filter'])) as $line) {
        if (is_array($line)) {
            $connectionNumber[] = '<a href="#" onClick="$(\'param\').value=\''.'conn='.$line["conn"].'\'; pushSearch(); return false">'.$line["conn"].'</a>';
            $action[] = '<a href="#" onClick="$(\'param\').value=\''.$line["op"].'\'; pushSearch(); return false">'.$line["op"].'</a>';
            $extra[] = $line["extra"];
            $dateparsed = strftime('%b %d %H:%M:%S',$line["time"]);
            $date[] = str_replace(" ", "&nbsp;", $dateparsed);
            if ($line["opfd"] == "op") {
                $oparr[] = $line["opfdnum"];
            } else {
                $oparr[] = "";
            }
        } else {
            $connectionNumber[] = "";
            $action[] = "";
            $date[] = "";
            $oparr[] = "";
            $extra[] = $line;
        }
    }
}

$n = new UserInfos($date,_("Date"),"1px");
$n->addExtraInfo($connectionNumber,_("Connection"),"1px");
$n->addExtraInfo($oparr,_("Operation"),"1px");
$n->addExtraInfo($action,_("Actions"),"1px");
$n->addExtraInfo($extra,_("Extra informations"));
$n->end= 200;
$n->first_elt_padding = 1;
$n->display(0,0);

?>
</div>

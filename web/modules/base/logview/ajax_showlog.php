<? if ($_SESSION['__notify'])  { ?>
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

foreach (xmlCall("base.getLdapLog",array($_SESSION['ajax']['filter'])) as $line) {
    if (is_array($line)) {

    $connectionNumber[] = '<a href="#" onClick="$(\'param\').value=\''.'conn='.$line[3].'\'; pushSearch(); return false">'.$line[3].'</a>';
    $action[] = '<a href="#" onClick="$(\'param\').value=\''.$line[6].'\'; pushSearch(); return false">'.$line[6].'</a>';
    $extra[] = $line[7];
    $date[] = strftime('%b %d %H:%M:%S',$line[0]);
    if ($line[4]=='op') {
            $oparr[]=$line[5];
        } else {
            $oparr[]="";
        }

    } else {

    $connectionNumber[] = "";
    $action[] = "";
    $date[] = "";
    $oparr[] = "";
    $extra[] = $line;
    }
}


$n = new UserInfos($connectionNumber,_("Connection"),"1px");

$n->addExtraInfo($oparr,_("Operation"),"1px");

$n->addExtraInfo($action,_("Actions"),"1px");

$n->addExtraInfo($extra,_("Extra informations"));
$n->addExtraInfo($date,_("Date"),"50px");


//$n->setName(_("LDAP log lines"));

$n->end= 200;
$n->first_elt_padding = 1;

$n->display(0,0);

?>
</div>
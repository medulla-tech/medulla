<?php
if (isset($_POST["bconfirm"])) {

    header("Location: " . urlStrRedirect("xmppmaster/xmppmaster/reloaddeploy", $_POST));
    exit;
}

unset($_GET['action']);
unset($_GET['submod']);
unset($_GET['module']);
unset($_GET['mod']);

if(isset($_GET['hostname'])){
  $f = new PopupForm(_T("Reload ".htmlentities($_GET['title'])." on machine ".htmlentities($_GET['hostname']),"xmppmaster"), 'popupReloadDeploy');
}
if(isset($_GET['cn'])){
  $f = new PopupForm(_T("Reload ".htmlentities($_GET['title'])." on machine ".htmlentities($_GET['cn']),"xmppmaster"), 'popupReloadDeploy');
}
else{
  $f = new PopupForm(_T("Reload the deployment","xmppmaster"), 'popupReloadDeploy');
}
foreach($_GET as $key=>$value){
  if($key != "cn" || $key != "hostname"){
      $f->add(new HiddenTpl($key), array("value" => $value, "hide" => True));
  }
}

if (isset($_GET['hostname'])){
    $f->add(new HiddenTpl("hostname"), array("value" => $_GET['hostname'], "hide" => True));
}
else if (isset($_GET['cn'])){
    $f->add(new HiddenTpl("hostname"), array("value" => $_GET['cn'], "hide" => True));
}

$f->add(new HiddenTpl("login"), array("value" => $_SESSION['login'], "hide" => True));

$force = new TrFormElement(_T("Force re-deployment during initial validity period", "xmppmaster"), new CheckboxTpl("force"));

$f->add($force, ["value"=>""]);
$date = $_GET['startcmd'];
$reschedule = new TrFormElement('<br>'._T("Rechedule deployment between now and 1 day", "xmppmaster"), new CheckboxTpl("reschedule"));
$f->add($reschedule, ["value"=>""]);

$f->addValidateButton("bconfirm");
$f->addCancelButton("bback");
$f->display();
?>

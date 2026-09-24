<?php
if (isset($_POST["bconfirm"])) {
    verifyCSRFToken($_POST);

    header("Location: " . urlStrRedirect("xmppmaster/xmppmaster/reloaddeploy", $_POST));
    exit;
}

if(isset($_GET['hostname'])){
  $f = new PopupForm(_T("Reload ".htmlentities($_GET['title'])." on machine ".htmlentities($_GET['hostname']),"xmppmaster"), 'popupReloadDeploy');
}
if(isset($_GET['cn'])){
  $f = new PopupForm(_T("Reload ".htmlentities($_GET['title'])." on machine ".htmlentities($_GET['cn']),"xmppmaster"), 'popupReloadDeploy');
}
else{
  $f = new PopupForm(_T("Reload the deployment","xmppmaster"), 'popupReloadDeploy');
}
// Keep module/submod/action in $_GET so the Confirm button passes its ACL
// check; just don't forward them (nor cn/hostname, added below) as hidden fields.
$skipHidden = array("module", "submod", "action", "mod", "cn", "hostname");
foreach($_GET as $key=>$value){
  if(in_array($key, $skipHidden)){
      continue;
  }
  $f->add(new HiddenTpl($key), array("value" => $value, "hide" => True));
}

if (isset($_GET['hostname'])){
    $f->add(new HiddenTpl("hostname"), array("value" => $_GET['hostname'], "hide" => True));
}
else if (isset($_GET['cn'])){
    $f->add(new HiddenTpl("hostname"), array("value" => $_GET['cn'], "hide" => True));
}

$f->add(new HiddenTpl("login"), array("value" => $_SESSION['login'], "hide" => True));

$force = new TrFormElement(_T("Force re-deployment during initial validity period", "xmppmaster"), new CheckboxTpl("force"));
$reschedule = new TrFormElement(_T("Rechedule deployment between now and 1 day", "xmppmaster"), new CheckboxTpl("reschedule"));

$f->push(new Table());
$f->add($force, ["value"=>""]);
$f->add($reschedule, ["value"=>""]);
$f->pop();

$f->addValidateButton("bconfirm");
$f->addCancelButton("bback");
$f->display();
?>

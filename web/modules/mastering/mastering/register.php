<?php
$entity = isset($_GET["entity"]) ? $_GET["entity"] : "";
$server = isset($_GET["server"]) ? $_GET["server"] : "";
$uuid = isset($_GET["uuid"]) ? $_GET["uuid"] : "";
$gid = isset($_GET["gid"]) ? $_GET["gid"] : "";
$name = isset($_GET["name"]) ? $_GET["name"] : "";


if(isset($_GET["uuid"])){
    $mode = "machine";
    $p = new PageGenerator(sprintf(_T("Register Action for Machine %s on entity %s, server %s", "mastering"), $name, $entity, $server));

}
else if (isset($_GET["gid"])){
    $mode = "group";
    $p = new PageGenerator(sprintf(_T("Register Action for Group %s on entity %s, server %s", "mastering"), $name, $entity, $server));
}
else{
    $mode = "new";
    $p = new PageGenerator(sprintf(_T("Register Action for New Machine on entity %s, server %s", "mastering"), $entity, $server));
}

$p->display();

$params = [
    "name"=>$name,
    "server"=>$server,
    "entity"=>$entity,
    "gid"=>$gid,
    "uuid"=>$uuid,
];

$f = new ValidatingForm(["action"=>urlStrRedirect("mastering/mastering/addAction", $params)]);

$f->push(new Table());
// Begin date
$beginDate = date("Y-m-d H:i:s", time());
$f->add(new TrFormElement(_T("Begin Date", "mastering"), new DateTimeTpl('begin_date')), ['value'=>$beginDate]);
// End date
$delta = 24*60*60; // delta +1 day
$endDate = date("Y-m-d H:i:s", time()+$delta);
$f->add(new TrFormElement(_T("End Date", "mastering"), new DateTimeTpl('end_date')), ['value'=>$endDate]);

// auth
$check = new CheckboxTpl("auth");
$login = new InputTpl("login");
$password = new PasswordTpl(("password"));

$fields = [
    $check,
    $login,
    $password
];

$values = [
    "",
    "",
    ""
];

$placeholders = [
    "",
    _T("Login", "mastering"),
    _T("Password", "mastering"),
];

$f->add(new TrFormElement(_T("Auth", "mastering"), new multifieldTpl($fields)), ["value" => $values, "placeholder"=>$placeholders] );
// $f->add(new TrFormElement(_T("Login", "mastering"), $login), ["disabled"=>"disabled"] );
// $f->add(new TrFormElement(_T("Password", "mastering"), $password), ["disabled"=>"disabled"] );
$f->pop();

$f->add(new HiddenTpl("add"), ["value"=>"register", "hide"=>true]);
$f->add(new HiddenTpl("server"), ["value"=>$server, "hide"=>true]);
$f->add(new HiddenTpl("gid"), ["value" => $gid, "hide"=>true]);
// $f->add(new HiddenTpl("targetName"), ["value" => $targetName, "hide"=>true]);
$f->add(new HiddenTpl("uuid"), ["value" => $uuid, "hide"=>true]);
$f->add(new HiddenTpl("entity"), ["value" => $entity, "hide"=>true]);
$f->add(new HiddenTpl("name"), ["value"=>$name, "hide"=>true]);

$f->pop();

$f->addValidateButton(_T("Confirm", "mastering"));
// $f->addCancelButton(_T("Cancel", "mastering"));
$f->display();

// Validate
?>
<script>
    toggleAuth = ()=>{

        if(jQuery("#auth").is(":checked")){
            jQuery("#login").attr("disabled", false);
            jQuery("#password").attr("disabled", false);
        }
        else{
            jQuery("#login").attr("disabled", true);
            jQuery("#password").attr("disabled", true);
        }
    }

    jQuery("#auth").on("click", ()=>{
        toggleAuth();
    })

    toggleAuth();
</script>

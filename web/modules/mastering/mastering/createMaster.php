<?php
$mode = "";

$server = (isset($_GET["server"])) ? htmlentities($_GET["server"]) : "";
$entity = (isset($_GET["entity"])) ? htmlentities($_GET["entity"]) : "";
$gid = (isset($_GET["gid"])) ? htmlentities($_GET["gid"]) : "";
$uuid = (isset($_GET["uuid"])) ? htmlentities($_GET["uuid"]) : "";
$name = (isset($_GET["name"])) ? $_GET["name"] : "";
$target = (isset($_GET["target"])) ? $_GET["target"] : "";

if($uuid != ""){
    $mode = "machine";
    $p = new PageGenerator(sprintf(_T("Create Master for Machine %s on entity %s, server %s", "mastering"), $target, $entity, $server));
}
elseif ($gid != ""){
    $mode = "group";
    $p = new PageGenerator(sprintf(_T("Create Master for Group %s on entity %s, server %s", "mastering"), $target, $entity, $server));

}
else{
    $mode = "new";
    $p = new PageGenerator(sprintf(_T("Create Master for New Machine on entity %s, server %s", "mastering"), $entity, $server));
}

$p->display();


$f = new ValidatingForm(["action"=>urlStrRedirect("mastering/mastering/addAction")]);
$f->push(new Table());


$f->add(new TrFormElement(_T("Master Name", "mastering"), new InputTpl("mastername")), ["placeholder"=>_T("Master Name", "mastering")]);
$f->add(new TrFormElement(_T("Description", "mastering"), new InputTpl("masterdescription")), ["placeholder"=>_T("Description", "mastering")]);

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
$f->pop();

$f->add(new HiddenTpl("add"), ["value"=>"mastering", "hide"=>true]);
$f->add(new HiddenTpl("server"), ["value"=>$server, "hide"=>true]);
$f->add(new HiddenTpl("gid"), ["value"=>$gid, "hide"=>true]);
$f->add(new HiddenTpl("uuid"), ["value"=>$uuid, "hide"=>true]);
$f->add(new HiddenTpl("entity"), ["value"=>$entity, "hide"=>true]);
$f->add(new HiddenTpl("name"), ["value"=>$name, "hide"=>true]);

$f->pop();
$f->addValidateButton(_T("Confirm", "mastering"));

$f->display();
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

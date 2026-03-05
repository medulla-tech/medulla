<?php
$entity = "";
$mode = "";
$server = "";
$uuid = "";
$gid = "";

if(isset($_GET["server"])){
    $mode = "new";
    $server = htmlentities($_GET["server"]);
}

else if(isset($_GET["uuid"])){
    $mode = "machine";
    $uuid = htmlentities($_GET["uuid"]);
}

else if (isset($_GET["gid"])){
    $mode = "group";
    $gid = htmlentities($_GET["gid"]);
}

$p = new PageGenerator(_T("Register Action", "mastering"));
$p->display();

$f = new ValidatingForm(["action"=>urlStrRedirect("mastering/mastering/addAction")]);

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
$f->add(new HiddenTpl("targetName"), ["value" => $gid, "hide"=>true]);
$f->add(new HiddenTpl("uuid"), ["value" => $uuid, "hide"=>true]);
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

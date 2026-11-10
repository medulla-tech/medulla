<style>
#workflow{
    display:flex;
}
#workflow-available-actions{
    width:75%;
}
#workflow-selected-actions{
    width:100%;
}

.workflow-list{
    min-width: 3vh;
    min-height: 48px;
    padding: 6px;
}

</style>
<?php
require_once("modules/mastering/includes/xmlrpc.php");

$entity = (isset($_GET["entity"])) ? htmlentities($_GET["entity"]) : "";
$mode = "";
$server = (isset($_GET["server"])) ? htmlentities($_GET["server"]) : "";
$uuid = (isset($_GET["uuid"])) ? htmlentities($_GET["uuid"]) : "";
$gid = (isset($_GET["gid"])) ? htmlentities($_GET["gid"]) : "";
$target = (isset($_GET["target"])) ? htmlentities($_GET["target"]) : "";

if(isset($_GET["uuid"])){
    $mode = "machine";
}

else if (isset($_GET["gid"])){
    $mode = "group";
}

else{
    $mode = "new";
}

$p = new PageGenerator(_T("Deploy Master Action", "mastering"));
$p->display();

$f = new ValidatingForm(["action"=>urlStrRedirect("mastering/mastering/addAction")]);

$f->push(new Table());
$f->add(new HiddenTpl("add"), ["value"=>"deploy", "hide"=>true]);
$f->add(new HiddenTpl("entity"), ["value"=>$entity, "hide"=>true]);
$f->add(new HiddenTpl("server"), ["value"=>$server, "hide"=>true]);
$f->add(new HiddenTpl("uuid"), ["value"=>$uuid, "hide"=>true]);
$f->add(new HiddenTpl("gid"), ["value"=>$gid, "hide"=>true]);
$f->add(new HiddenTpl("target"), ["value"=>$target, "hide"=>true]);

// List of masters
$datas = (array)xmlrpc_get_masters_for_entity($entity, 0, -1, "");

$select_master = new SelectItem('select_master');
$select_master->setElements($datas["data"]["name"]);
$select_master->setElementsVal($datas["data"]["uuid"]);
$f->add(
    new TrFormElement(_T('Masters', 'mastering'), $select_master), array("value" => '')
);

// Begin date
$beginDate = date("Y-m-d H:i:s", time());
$f->add(new TrFormElement(_T("Begin Date", "mastering"), new DateTimeTpl('begin_date')), ['value'=>$beginDate]);

// End date
$delta = 24*60*60; // delta +1 day
$endDate = date("Y-m-d H:i:s", time()+$delta);
$f->add(new TrFormElement(_T("End Date", "mastering"), new DateTimeTpl('end_date')), ['value'=>$endDate]);

// Hostname not known: add a template input
if($mode == "new"){
    $radioTpl = new RadioTpl("hostname-selector");
    $radioTpl->setChoices([_T("Ask during masterisation", "master"), _T("Setup a template", "master")]);
    $radioTpl->setValues(["ask", "template"]);

    $f->add(new TrFormElement(_T("machine hostname", "mastering"), $radioTpl));
    $f->add(new TrFormElement(_T("Template name", "mastering"), new InputTpl("hostname-template")));
}

$scripts = xmlrpc_get_summary_scripts_list($entity);

$availables = "";
foreach($scripts as $script){
    $availables .= '<li class="workflow-action">'.htmlentities($script["name"]).' - '.htmlentities($script["description"]).'<input class="action-value" type="hidden" name="workflow-types[]" value="script" disabled /><input class="action-value" type="hidden" name="workflow-values[]" value="'.htmlentities($script["id"]).'" disabled /></li>';
}

// Workflow
$f->add(
    new MergedTrFormElement(_T("Workflow Editor", "mastering"), new SpanElement('
<div id="workflow">
    <div id="workflow-available-actions">
        <h3>Available</h3>
        <ul class="workflow-list" id="workflow-available-actions-list">
            '.$availables.'
        </ul>
    </div>

    <div id="workflow-selected-actions">
        <h3>Selected</h3>
        <ul class="workflow-list" id="workflow-selected-actions-list">
            <li class="workflow-action"><b>Deploy Master</b><input class="action-value" type="hidden" name="workflow-types[]" value="action"/><input class="action-value" type="hidden" name="workflow-values[]" value="deploy" /></li>
        </ul>
    </div>
</div>
', "mastering") )// /TrFormElement
); // /add


// $f->add(new TrFormElement(_T("Master Name", "mastering"), new InputTpl("mastername")), ["placeholder"=>_T("Master Name", "mastering")]);
$f->addValidateButton(_T("Confirm", "mastering"));
$f->display();

?>
<script>

jQuery( function() {

    // template selector init

    hostnameSelector = jQuery("input[name='hostname-selector']:checked").val()
    console.log(hostnameSelector)
    if(hostnameSelector == "ask"){
        jQuery(jQuery("#hostname-template").parent().parent().parent()).hide()
    }

    jQuery("input[name='hostname-selector']").on("change", ()=>{
        hostnameSelector = jQuery("input[name='hostname-selector']:checked").val();

        jQuery(jQuery("#hostname-template").parent().parent().parent()).toggle()
    });


    // Workflow mecanics
    var lists = jQuery("#workflow-available-actions-list, #workflow-selected-actions-list");

    function syncActionValues() {
        jQuery("#workflow-available-actions-list .workflow-action").each(function() {
            jQuery(this).find(".action-value").prop("disabled", true);
        });

        jQuery("#workflow-selected-actions-list .workflow-action").each(function() {
            jQuery(this).find(".action-value").prop("disabled", false);
        });
    }

    lists.sortable({
        connectWith: ".workflow-list",
        dropOnEmpty: true,
        items: "> li.workflow-action",
        placeholder: "ui-state-highlight",
        forcePlaceholderSize: true,
        tolerance: "pointer",
        revert: 150,
        receive: function() {
            syncActionValues();
        },
        remove: function() {
            syncActionValues();
        },
        update: function() {
            syncActionValues();
        }
    });

    lists.disableSelection();
    syncActionValues();
} );
</script>

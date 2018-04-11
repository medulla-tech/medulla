jQuery("#bvalid").click(function() {
    if(jQuery("#name").val() == "")
    {
        jQuery("#name").focus();
    }
    else
        sendForm();

});

function sendForm(){

    var action = jQuery("[name='action']").val()
    if(action == 'undefined')
        var url = "modules/kiosk/kiosk/ajaxAddProfile.php";
    else
    {
        action = action[0].toUpperCase() + action.substring(1)
        var url = "modules/kiosk/kiosk/ajax"+action+"Profile.php";
    }


    // Create json which contains all the needed infos
    var datas = {};
    datas['name'] = jQuery("#name").val();
    datas['active'] = jQuery("#status").val();
    datas['id'] = jQuery("[name='id']").val();

    datas['packages'] = generate_json();

    // Send the infos to ajaxAddProfile.php
    jQuery.post(url, datas, function(result){
        // the datas printed in ajaxAddProfile.php are stored in result
        alert(result)
    });
}
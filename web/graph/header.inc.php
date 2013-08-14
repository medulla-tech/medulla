<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
 *
 * This file is part of Mandriva Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 */

$root = $conf["global"]["root"];

?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Mandriva Management Console</title>
    <link href="graph/master.css" rel="stylesheet" media="screen" type="text/css" />
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta http-equiv="imagetoolbar" content="false" />
    <meta name="Description" content="" />
    <meta name="Keywords" content="" />
    <link rel="icon" href="img/common/favicon.ico" />
    <script src="jsframework/lib/jquery-1.10.2.min.js" type="text/javascript"></script>
    <script src="jsframework/lib/jquery.cookie.js" type="text/javascript"></script>
    <script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.3/jquery-ui.min.js"></script>
    <script type="text/javascript">
    // Avoid prototype <> jQuery conflicts
    jQuery.noConflict();
    </script>
    <script src="jsframework/lib/prototype.js" type="text/javascript"></script>
    <script src="jsframework/src/scriptaculous.js" type="text/javascript"></script>
    <script src="jsframework/common.js" type="text/javascript"></script>
    <link rel="stylesheet" href="jsframework/lib/jquery.ui.css" />
    <script src="jsframework/lib/jquery.loadmask.js" type="text/javascript"></script>
    <link href='jsframework/lib/jquery.loadmask.css' rel='stylesheet' type='text/css'>
    <script src="jsframework/lib/jquery.mousewheel-3.0.6.pack.js" type="text/javascript"></script>
<?php
unset($css);
?>
<script type="text/javascript">
<!--

//jQuery ajax response handlers
function ajaxSend(){
    jQuery('#loadimg').attr('src','<?php echo $root; ?>img/common/loader_p.gif');
    try
    {
        jQuery('#container').mask("");
        jQuery('#container').width('100%');
    }
    catch(err)
    {
        console.log('Error masking')
    }

}

function ajaxComplete(){
    if (!jQuery.active && !jQuery.ajax.active){
        jQuery('#loadimg').attr('src','<?php echo $root; ?>img/common/loader.gif');
        jQuery('#container').unmask();
    }
}

// prefix: checkbox prefix, check_state 0/1
function checkAll (prefix, check_state) {
    jQuery('input[type=checkbox]').each(function(){
        if (jQuery(this).attr('name').indexOf(prefix) > -1 )
            jQuery(this).prop('checked', check_state);
    });
}

// prefix: radio prefix, value null,ro,rw
function checkAllRadio (prefix, value) {
    jQuery('input[type=radio]').each(function(){
        if (jQuery(this).attr('name').indexOf(prefix) > -1 && jQuery(this).val() == value)
            jQuery(this).prop('checked', 1);
    });
}

// select all select with class 'list' options in the page
// usefull to run before post a form with
// selects in it.
function selectAll(formId) {
    jQuery("#" + formId + " select.list option").prop('selected', 'selected');
}


jQuery(function(){
    // Popup window Close button action
    jQuery('a.popup_close_btn').click(function(){
        closePopup();
    });
    
    // Ajax handlers
    jQuery(document).bind("ajaxSend",ajaxSend).bind("ajaxStop",ajaxComplete);
    
});

// Popup under mouseevent
function _defaultPlacement(evt){
    var left = Math.max(0,evt.clientX - jQuery('#popup').outerWidth()+ jQuery(window).scrollLeft());
    var top = Math.max(0, evt.clientY + jQuery(window).scrollTop());
    jQuery('#popup').css({'left': left+"px",'top':top+"px"});
}

function _centerPlacement(evt){

    jQuery('#popup').css({
        'width': '50%',
        'left': '25%',
        'top':'15%'
    });
    jQuery('#overlay').fadeIn().click(closePopup);
}

function PopupWindow(evt, url, width,callback,content) {
    jQuery('#popup').css("width", width + "px" );
    if (!evt) evt = window.event;
    
    // If content is specified, we skip ajax request
    if (content){
        jQuery("#__popup_container").html(content);
        
        callback = callback || _defaultPlacement;
        callback(evt);
        jQuery('#popup').fadeIn();
        return;
    }
    
    jQuery.ajax({
        'url': url,
        type: 'get',
        success: function(data){
            jQuery("#__popup_container").html(data);
        },
        error: function(e){
            jQuery("#__popup_container").html('Could not load content, please check your network connection.');
        },
        complete: function(){
            // If height > 300, we force using center mode
            if (jQuery('#popup').outerHeight() > 300 && !callback)
                callback = _centerPlacement;
            callback = callback || _defaultPlacement;
            callback(evt);
            jQuery('#popup').fadeIn();
        }
    });
}

function showPopup(evt, url) {
    PopupWindow(evt, url, 300);
}

function showPopupFav(evt,url) {
    PopupWindow(evt, url, 200,function(evt){
    var left = Math.max(0,evt.clientX - 100 + jQuery(window).scrollLeft());
    var top = Math.max(0, evt.clientY + jQuery(window).scrollTop());
    jQuery('#popup').css({'left': left+"px",'top':top+"px"});
    });
}

function showPopupUp(evt,url) {
    PopupWindow(evt, url, 300,function(evt){
    var left = Math.max(0,evt.clientX - jQuery('#popup').outerWidth()+ jQuery(window).scrollLeft());
    var top = Math.max(0, evt.clientY - jQuery('#popup').outerHeight()+ jQuery(window).scrollTop());
    jQuery('#popup').css({'left': left+"px",'top':top+"px"});
    });
}

function showPopupCenter(url) {
    PopupWindow(null, url, 300,_centerPlacement);
}

function displayConfirmationPopup(message, url_yes, url_no, klass) {
    
    if (!klass) var klass = '';
    var message = '<div style="padding: 10px"><div class="alert alert-info ' + klass + '">' + message + '</div>';
    message += '<div style="text-align: center"><a class="btn btn-primary" href="' + url_yes + '"><?=_('Yes')?></a>';

    if (url_no)
        message += ' <a class="btn" href="' + url_no + '"><?=_('No')?></a>';
    else
        message += ' <button class="btn" onclick="closePopup(); return false;"><?=_('No')?></button>';

    message += '</div></div>';

    PopupWindow(null, null, 0,function(evt){

            jQuery('#popup').css({
                'width': '50%',
                'left': '25%',
                'top':'15%'
            });
            jQuery('#overlay').fadeIn().click(closePopup);
            
        },message);
}

// Replacement function for Javascript alert (override)
function alert(message, title, klass) {
    
    function nl2br (str, is_xhtml) {
        var breakTag = (is_xhtml || typeof is_xhtml === 'undefined') ? '<br />' : '<br>';
        return (str + '').replace(/([^>\r\n]?)(\r\n|\n\r|\r|\n)/g, '$1' + breakTag + '$2');
    }

    message = nl2br(message);
    
    if (!klass) klass = '';
    if (!title) title = '';
    var message = '<div style="padding: 10px"><div class="alert alert-error ' + klass + '">' + message + '</div>';
    //message += '<div style="text-align: center"><a class="btn btn-primary" href="' + url_yes + '"><?=_('Yes')?></a>';

    message += ' <center><button class="btn" onclick="closePopup(); return false;"><?=_('Close')?></button></center>';

    message += '</div></div>';

    PopupWindow(null, null, 0,function(evt){

            jQuery('#popup').css({
                'width': '50%',
                'left': '25%',
                'top':'15%'
            });
            jQuery('#overlay').fadeIn().click(closePopup);
            
        },message);
}

function closePopup() {
    jQuery('#popup').fadeOut();
    jQuery('#overlay').fadeOut();
}


function validateForm(formId,errmsg) {
    
    // By default, we show the error message
    if (errmsg == null ) errmsg = true;
    
    var err = 0;
    // Required fields
    jQuery('#'+formId).find('input[rel=required],textarea[rel=required],select[rel=required]').each(function(){
        if (jQuery(this).val() == ''){
            jQuery(this).addClass('form-error');
            err == 0 && jQuery(this);
            err = 1;
        }
        else
            jQuery(this).removeClass('form-error');
    });

    // Regexp fields
    jQuery('#'+formId).find('input[data-regexp],textarea[data-regexp]').each(function(){

        if (jQuery(this).val() && jQuery(this).attr('data-regexp') != '/.+/'){
            var flags = jQuery(this).attr('data-regexp').replace(/.*\/([gimy]*)$/, '$1');
            var pattern = jQuery(this).attr('data-regexp').replace(new RegExp('^/(.*?)/'+flags+'$'), '$1');

            var re = new RegExp(pattern, flags);

            if (!re.test(jQuery(this).val()))
            {
                err = 1;
                jQuery(this).addClass('form-error');
            }
            else
                jQuery(this).removeClass('form-error');
        }
    });

    // Particular case: password match
    if (jQuery('#pass').val() != null && jQuery('#confpass').val() != null)
        if (jQuery('#pass').val() != jQuery('#confpass').val()){
            err = 1;
            jQuery('#confpass').addClass('form-error');
        }
    
    if (errmsg && err != 0)
        alert('<?php echo  _("Form cannot be submit. Input errors are highlighted in red.") ?>');
    
    return err == 0;
}

<?php
if (isset($_SESSION['servicesInfos'])) {
?>
function restartServices() {

    services = JSON.parse('<?=$_SESSION['servicesInfos']?>');

    checkService = function(service) {
        jQuery.get({
            'url': service.check,
            type: 'get',
            success: function(data){
                var statusElem = jQuery('#'+service.id + 'Status');
                // If the response is json
                if(typeof data =='object'){
                    var status = data[1];
                    if (status != "active" && status != "failed") {
                        setTimeout(function() {
                            checkService(service);
                        }, 800);
                    }
                    else {
                        if (status == "failed") {
                            statusElem.html(service.msg_fail);
                            statusElem.removeClass("alert-info");
                            statusElem.addClass("alert-error");
                        }
                        else {
                            statusElem.html(service.msg_success);
                            statusElem.removeClass("alert-info");
                            statusElem.addClass("alert-success");
                        }
                    }
                }
                else {
                    statusElem.html(service.msg_fail);
                    statusElem.removeClass("alert-info");
                    statusElem.addClass("alert-error");
                }
        } });
        

    services.each(function(service) {
        jQuery.get({
            'url': service.restart,
            type: 'get',
            success: function(data){
                var message = jQuery('#'+service.id + 'Status');
                if (!message.length) {
                    message = jQuery('<p></p>').attr({'id': service.id + 'Status',
                                                'class': 'alert alert-info'}).appendTo('#restartStatus');
                }
                message.html(service.msg_exec);
                message.removeClass("alert-success");
                message.removeClass("alert-error");
                message.addClass("alert-info");
                jQuery('#restartStatus').show();
                setTimeout(function() {
                    checkService(service);
                }, 1000);
        } });

    });
}

}
<?php
}
?>

-->
</script>

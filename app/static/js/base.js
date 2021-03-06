/*
function escape_slug(slug) {
    return slug.replace(/:/g,"\\:").replace(/\./g,"\\.").replace(/-/g,"\\-");   
}
*/

var _ERR_MSG = gettext("An error ocurred while executing your request.\nJust in case, press F5 to refresh the page before trying again.");
var _NO = gettext("No");
var _YES = gettext("Yes");
var _OK = gettext("Ok");
var _CANCEL = gettext("Cancel");
var _CONFIRM = gettext("Are you sure?");
var _CONFIRM_T = gettext("Confirm");

$().toastmessage({
    position : 'bottom-center'
});

function loading(show) {
    if (show == undefined) {
        show = true;
    }
    if (show) {
        $.loading(true, {at: 'center', text: gettext("Working..."), loadingClass: 'context-loader', update: {texts: [gettext("Please, wait..."), gettext("Oops!, something went wrong.")]}});
    } else {
        $.loading(false);
    }
}
    
function show_ok_dialog(msg) {
    //msg = msg.replace(/\n/g,"<br/>");
    $.alerts.okButton = '&nbsp;'+_OK+'&nbsp;'
    jAlert(msg,_TITLE); 
}

function confirmSimple(callback, message) {
    confirmDialog(callback, message || _CONFIRM)
}

function confirmDialog(callback, msg) {
    $.alerts.okButton = '&nbsp;'+_YES+'&nbsp;'
    $.alerts.cancelButton = '&nbsp;'+_NO+'&nbsp;'
    jConfirm(msg, _CONFIRM_T, callback);
}

function update_favorites(url,path) {
    $.post(url,
            {path: path,
            title: document.title},
            process_update_favorites_response,
              "xml");   
}

function process_update_favorites_response(data) {
    $(data).find('response').each(function(){
        var id = $(this).find('id');
        var tit = $(this).find('title');
        var path = $(this).find('path');
        var c = $(this).find('content');
        if (c.length>0) {
            $("#favs").html(c.text());
        }
        if (tit.length>0) {
            elem = '<li id="bookmark_'+id.text()+'"><a href="'+path.text()+'">'+tit.text()+'</a></li>';
            $("#bookmark_container").append(elem);
        } else if (id.length>0) {
            $("#bookmark_"+id.text()).remove();
        }
    }); 
}

$(document).ready(function() {
    $('body').ajaxStart(function() {
        loading(true);
    }); 
    $('body').ajaxStop(function() {
        loading(false);
    });
    $("body").ajaxError(function(event, request, settings){
        show_ok_dialog(_ERR_MSG);
    });
    $("input[type='button'][name='href']").each(function() {
        $(this).click(function(){
            window.location.href = $(this).attr('rel')
        });
    });
    $("input[type='button'][name='confirm_href']").on('click', function() {
        elem = $(this);
        confirmSimple(function(r){
            if (r) {
                window.location.href = $(elem).attr('rel')
            }
        });
    }); 
    $("input[name='selector']").click( function() {
        $("#" + $(this).attr('rel') + " INPUT[type='checkbox']").attr('checked', $(this).is(':checked'));
    }); 
    $("*[title]:not(.field-error)").tipTip({delay: 200, defaultPosition: 'top'});
    $(".field-error").tooltip({className:'error-tip'});
    /*$(".tooltip").tipTip({delay: 200, defaultPosition: 'left'});*/
    $('body').ajaxComplete(function() {
        $("*[title]").tipTip({delay: 200, defaultPosition: 'top'});
        /*$(".tooltip").tipTip({delay: 200, defaultPosition: 'left'});*/
    });
    
});
function create_message_box() {
    $('#message-box-w li').each(
            function() {
                $(this).prepend("<span class='close_button'></span>");
            }
     );
    $('.close_button').on('click', function() {
        $(this).parent().remove();
    });
}
function popoverlay(message) {
    $.blockUI({
            message: '<span class="loading_message">'+message+'</span>',
            css: {
                'padding': '5px',
                '-webkit-border-radius': '5px', 
                '-moz-border-radius': '5px',
                'border-radius': '5px'
            }
        });     
}
function removeoverlay() {
    $.unblockUI();
}
function updateTips( t ) {
    $(".validateTips")
        .text( t )
        .addClass( "ui-state-highlight" );
    setTimeout(function() {
        $(".validateTips").removeClass( "ui-state-highlight", 1500 );
    }, 500 );
}

function checkLength( o, n, min, max ) {
    if ( o.val().length > max || o.val().length < min ) {
        o.addClass( "ui-state-error" );
        message = interpolate(gettext('Length of %s must be between %s and %s.'), [n, min, max])
        updateTips(message);
        return false;
    } else {
        return true;
    }
}

function checkRegexp( o, regexp, n ) {
    if ( !( regexp.test( o.val() ) ) ) {
        o.addClass( "ui-state-error" );
        updateTips( n );
        return false;
    } else {
        return true;
    }
}

function get_filename(value) {
    if (value == undefined || value == '') return '';
    return /([^\\]+)$/.exec(value)[1];
}

function query_user(text, callback) {
    $.post(_UQUERY, {'search': text}, callback, "json");         
}
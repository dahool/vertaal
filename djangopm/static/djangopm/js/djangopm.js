/*Copyright (c) 2013, Sergio Gabriel Teves
All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
function pm_delete(url) {
	if ($("#mailbox-content :checked").length > 0) {
		confirmSimple(function(r){
			if (r) {
				$.post(url, $("#mailbox-content :checked"), function(data) {
					$(data).find('response').each(function() {
						/*$(this).find('pk').each(function() {
							$("#mob_"+$(this).text()).remove();
						})*/
				        $('#mailbox-content').load($("#mailbox-menu li.active").attr('href'));
					});	
				},"xml");
			}
		}, gettext("Are you sure you want to delete the selected messages?"));		
	} else {
		show_ok_dialog(gettext("Please, select an element from the list."));
	}
}
function process_submit(ev, action) {
    var form = $(ev).find("#compose_form");
    data = $(form).serialize();
    data = data + "&action=" + action;
    $.post($(form).attr('action'), data, function(data) {
        $(data).find('response').each(function(){
            var m = $(this).find('message');
            if (m.length>0) {
                var t = $(m).find('text')
                if (t.length>0) {
                    var text = t.text();
                } else {
                    var text = m.text();
                }
                t = $(m).find('type')
                if (t.length>0) {
                    var type = t.text();
                } else {
                    var type = 'notice';
                }
                $().toastmessage('showToast', {text : text, type : type});          
            }
            var c = $(this).find('content');
            if (c.length>0) {
                $(ev).html(c.text());
                $('#id_message').height($(ev).dialog( "widget" ).height()-170);
            } else {
                $(ev).dialog('close');
                $("#mailbox-menu li.active").click();
            }
        }); 
    },"xml");
}
function compose_new(load) {
    $("#compose_form").find(":text, textarea").val('');
    $('#compose_recipients > .pm_recipient').remove();
    $('#compose_recipients > .placeholder').show();
    $("#compose_form > input[name='recipients']").remove();
    $("#compose_form > input[name='id']").remove();
    if (load != undefined) {
    	$("#pm_compose").load(load, function() {
    		$("#pm_compose").dialog('open');
    		var v = $("#id_message").val();
    		$("#id_message").focus().val("").val(v);
    	});	
    } else {
    	$("#pm_compose").dialog('open');	
    }
}
function process_query_response(data) {
    $(data).find('response').each(function(){
        var m = $(this).find('message');
        if (m.length>0) {
            show_ok_dialog('query_d', m.text());
        }
        var c = $(this).find('content');
        if (c.length>0) {
            $("#search-results").html(c.text());
            add_listener();
        }
    }); 
}   
$(function() {
    
    var $formact = $("#form-action");
    var $mboxmenu = $("#mailbox-menu");
    var $mboxct = $("#mailbox-content");
    
    $mboxct.width($formact.width()-$mboxmenu.width());
    
    $("#mailbox-menu li[href]").on('click', function() {
        $("#mailbox-menu li.active").removeClass("active");
        $(this).addClass("active");
        $('#mailbox-content').load($(this).attr('href'));
    });
    
    $("#mailbox-content").on("click","input[type=checkbox]", function(ev) {
        ev.stopPropagation();
    });
    
    $("#mailbox-content").on('click', 'li[href]', function() {
        if ($(this).attr('compose')=='compose') {
            $("#pm_compose").load($(this).attr('href'), function() {
                $('#pm_compose').dialog('open');    
            });
        } else {
            $("#pm_detail").html('');
            $("#pm_detail").dialog('open');
            $("#pm_detail").load($(this).attr('href'));
            $(this).removeClass('unread');
        }
    });
    
    $("button[action=pm_delete]").click(function(ev) {
        pm_delete($("#message_delete_target").attr('href'));
    });
    $("button[action=pm_compose]").click(function(ev) {
        compose_new();
    });

    $("#pm_compose").on('click', '.pm_recipient', function() {
        var elem = $(this).attr('id');
        $(this).mouseout();
        $(this).remove();
        $("input[id=input_"+elem+"]").remove();
        if ($('#compose_recipients > .pm_recipient').length == 0) {
            $('#compose_recipients > .placeholder').show();    
        }
    });
    
    $("#pm_detail").on('click', '.pm_detail_from a', function(ev) {
        ev.preventDefault();
        url = $(this).attr('href');
        $("#pm_detail").dialog('close');
        compose_new($(this).attr('href'));
    });
    
    $("#pm_compose").on('click', '.pm-to-search-result li', function() {
    	if ($('#to_' + $(this).attr('value')).length > 0) {
    		return false;
    	}
        $('<span/>', {
            html: $(this).text(),
            title: gettext('Remove'),
            id: 'to_' + $(this).attr('value') 
        }).addClass('pm_recipient').appendTo('#compose_recipients');
        $('#compose_recipients > .placeholder').hide();
        $(".pm-to-search-result").remove();
        $('<input/>', {
            type: 'hidden',
            value: $(this).attr('value'),
            id: 'input_to_' + $(this).attr('value'),
            name: 'recipients'
        }).appendTo('#compose_form');
    });
    
	$("#mailbox-content").on('click', 'div.pagination a', function(ev) {
		ev.preventDefault();
		$('#mailbox-content').load($("#mailbox-menu li.active").attr('href') + $(this).attr('href'));
	});
	
    $("#pm_compose").on('click', "a[href=#pm_add_recipient]", function(ev) {
        ev.preventDefault();
        var si = $('<input/>', {
            type: 'text',
            val: '',
        })
        .addClass("pm-corner-all pm-form-input pm-to-search")
        .on('blur', function(e) {
            $("#compose_recipients").show();
            $(this).remove();
        })
        .on('keyup', function(e) {
            if ($(this).val().length >= 3) {
                $(".pm-to-search-result").remove();
                var pos = $(this).position();
                var height = $(this).height();
                var width = $(this).width();
                query_user($(this).val(), function(data) {
                    var rpanel = $('<div/>').addClass('pm-to-search-result').css('top', pos.top+height+5).css('left', pos.left).width(width/2);
                    var list = '<ul>';
                    $.each(data.result, function(i, obj) {
                        list = list + '<li value="'+obj.pk+'">'+obj.username+'</li>';
                    });
                    list = list + '</ul>';
                    $(list).appendTo(rpanel);
                    rpanel.appendTo('#pm_compose');
                })
            }
        });
        $("#compose_recipients").hide();
        $("#compose_recipients").after(si);
        $(si).focus();
    });
    
    $("#pm_detail").dialog({
        autoOpen: false,
        modal: true,
        resizable: true,
        width: 700,
        height: 400
    });

    $("#pm_compose").dialog({
        autoOpen: false,
        modal: true,
        resizable: true,
        width: 700,
        height: 400,
        buttons: [
            {
		    text: gettext("Send"),
		    icons: { primary: "pm-icon-send"},
		    click: function() {
		        process_submit(this, 'send');
		        }
		    },                  
            {
            text: gettext("Save"),
            icons: { primary: "pm-icon-save"},
            click: function() {
                    process_submit(this, 'save');
                }
            },{
            text: gettext("Close"),
            icons: { primary: "pm-icon-cancel"},
            click: function() {
                    $( this ).dialog( "close" );
                }
            }
         ],
    }).bind('dialogopen', function(ev, ui) {
        $('#id_message').height(225);  
        if ($('#compose_recipients > .pm_recipient').length == 0) {
            $('#compose_recipients > .placeholder').show();    
        }
    }).bind("dialogresize", function(event, ui) {
        $('#id_message').height(ui.size.height-170);
    });
    
    $mboxct.show('slow');
});

function query_user(text, callback) {
    $.post(_UQUERY, {'search': text}, callback, "json");         
}
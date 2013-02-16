//Copyright (c) 2013, Sergio Gabriel Teves
//All rights reserved.
//
//This program is free software: you can redistribute it and/or modify
//it under the terms of the GNU General Public License as published by
//the Free Software Foundation, either version 3 of the License, or
//(at your option) any later version.
//
//This program is distributed in the hope that it will be useful,
//but WITHOUT ANY WARRANTY; without even the implied warranty of
//MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//GNU General Public License for more details.
//
//You should have received a copy of the GNU General Public License
//along with this program.  If not, see <http://www.gnu.org/licenses/>.

function pm_delete(url) {
	if ($(".mailboxtable :checked").length > 0) {
		confirmSimple(function(r){
			if (r) {
				$.post(url, $(".mailboxtable :checked"), function(data) {
					$(data).find('response').each(function() {
						$(this).find('pk').each(function() {
							$("#mob_"+$(this).text()).remove();
						})
					});	
				},"xml");
			}
		});		
	} else {
		show_ok_dialog(gettext("Please, select an element from the list."));
	}
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
    
    $("#mailbox-content").on('click', 'li[href]', function() {
        $("#pm_detail").html('');
        $("#pm_detail").dialog('open');
        $("#pm_detail").load($(this).attr('href'));
        //$("#mailbox-menu li.active").click();
        $(this).removeClass('unread');
    });
    
    $("#pm_detail").dialog({
        autoOpen: false,
        modal: true,
        resizable: true,
        width: 700,
        height: 400
    });
    
    /*
	$("#mailbox").show();
	$("#mailbox").on( "tabsactivate", function(event, ui) {
		var panel = ui.newPanel;
		if ($(panel).find('.mailboxtable').length == 0) loadPanel(panel);
	});
	loadPanel($("#pminbox"));
	
	$(".mailbox_holder").on("click","tr[alt]", function(ev) {
		var elem = $($(this).attr('alt'));
		if ($(this).hasClass('pm_unread') && !$(elem).is(":visible")) {
			$this = $(this);
			$.post($(elem).attr('href'), function() {
				$this.removeClass('pm_unread');
			});
		}
		$(elem).toggle();
	});
	
	$(".mailbox_holder").on("click","tr[id^='inbox_detail']", function(ev) {
		$(this).hide();
	});

	$(".mailbox_holder").on("click","input[type=checkbox]", function(ev) {
		ev.stopPropagation();
	});
	
	$("#mailbox button[href^='#']").click(function(ev) {
		$($(this).attr('href')).dialog('open');
	});
	
	$("button[action=pm_delete]").click(function(ev) {
		pm_delete($(this).attr('href'));
	});
	
	$("#pm_detail").dialog({
	    autoOpen: false,
	    modal: true,
	    resizable: true,
	});

	var _SAVE = gettext("Save");
	var _SEND = gettext("Send");
	var _CLOSE = gettext("Close");
	
	$("#pm_compose").dialog({
	    autoOpen: false,
	    modal: true,
	    resizable: true,
	    buttons: [{
	    	text: _SAVE,
	    	click: function() {
	    	},
	    	text: _SEND,
	    	click: function() {
	    	},
	    	text: _CLOSE
	    	click: function() {
	    		$( this ).dialog( "close" );
	    	},
	    }],

	});*/
	
});



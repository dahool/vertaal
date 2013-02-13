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

function loadPanel(panel) {
	var url = $(panel).attr('href');
	$(panel).find('.mailbox_holder').load(url);
	/*
	$.post(url, function(data) {
		$(panel).find('.mailbox_holder').html(data);
	},"html");*/
}
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
	//$("#mailbox").tabs();
	//$("#mailbox button").button();
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
		/*
		$("#pm_detail").load($(this).attr('href'), function() {
			$("#pm_detail").dialog('open');
		})*/
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
	    /*open: function() {
	        $("#id_comment").val('');
	    },
	    close: function() {
	        $("#id_comment").removeClass( "ui-state-error" );
	        $("#upload_form div.error-tip").remove();
	        $("span.error").remove();
	    }*/
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
	    /*open: function() {
	        $("#id_comment").val('');
	    },
	    close: function() {
	        $("#id_comment").removeClass( "ui-state-error" );
	        $("#upload_form div.error-tip").remove();
	        $("span.error").remove();
	    }*/
	});
	
});



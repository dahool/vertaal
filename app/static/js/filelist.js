var current_id = false;

function check_current() {
	if (current_id) {
		$('#lock_comment_'+current_id).hide()
		$('#lock_break_'+current_id).show();
		$('#comment_'+current_id).unbind('keypress');
	}
}
function init_select_events() {
	var div = $('#user-selection-list');
    $(document).keyup(function(event){
	    if (event.keyCode == 27) {
	    	$(div).hide();
	    }
	});
}

function select_user(elem, callback, param) {
    var topOffset = -10;
    var leftOffset = -210;

    var div = $('#user-selection-list');
    $(div).hide();
    $(div).on('submit', function() {
		$(this).hide();
		$(this).off('submit');
		callback(param,{userid:$('#user-select').val()});
    }).on('hide', function() {
    	$(this).off('submit');
    })
    
	var p = $(elem).position();
	div.css("position","absolute");
	div.css("top",(p.top+topOffset)+"px");
	div.css("left",(p.left+leftOffset)+"px");
    div.css("width","210px");
	div.show();
        
}
function try_toggle(url, opc) {
	data = {}
	if (opc!=undefined) {
		data = opc
	}
	check_current();
	$.post(url,
		  data,
		  process_toggle_response,
		  "xml");
}
function try_toggle_cnf(url, opc) {
	confirmSimple(function(r){
		if (r) {
			try_toggle(url, opc);
		}
	});
}
function show_file_dialog(msg) {
	show_ok_dialog(msg);
}
function process_toggle_response(data) {
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
			//show_file_dialog(m.text());
		}
		var c = $(this).find('content');
		var id = $(this).find('id');
		if (c.length>0) {
			$("#file_row_"+id.text()).html(c.text());
		}
	});	
}
function add_comment(name, url) {
	$("#lock_comment").attr('action', url);
	$("#comment_text").text(interpolate(gettext('Unlocking file %s'), [name]));
	$("#lock_comment").dialog('open');
}
function load_component(url,replace, postData) {
    if (replace==undefined) replace = false;
    $.post(url, postData, function(data, status, xhr) {
        if (xhr.hasOwnProperty('responseJSON')) {
            show_ok_dialog(data.message);
        } else {
            $(data).find('tbody').each(function() {
                if (replace) {
                    $("#filestabs").find('tbody').html($(this).html());
                } else {
                    $("#filestabs").find('tbody').append($(this).html());
                }
            });
            $("#filestabs").find('table').trigger("update");
        }
    });    
}
function hide_component(name) {
    loading(true);
    $("#filestabs").find('tr[component="'+name+'"]').remove();
    loading(false);
}
function check_filter_button() {
    n = $("#component_list").find('input:checked');
    if (n.length == 1) {
        $(n).button('disable');
    } else {
        $(n).button('enable');
    }    
}
function init_filedialogs() {
    $("#comment_input").keyup(function (e) {
        if( e.keyCode == $.ui.keyCode.ENTER ) {
            e.preventDefault();
            $("#lock_comment ~ div.ui-dialog-buttonpane").find('button').click();
        }
    });
		
    $( "#lock_comment" ).dialog({
        autoOpen: false,
        width: 350,
        modal: true,
        resizable: false,
        buttons: [{
        	text: _OK,
        	click : function() {
                var bValid = true;
                bValid = bValid && checkLength( $("#comment_input"), gettext("Comments"), 4, 255 );
                if ( bValid ) {
                    try_toggle($("#lock_comment").attr('action'),{'text': $('#comment_input').val()});
                    $( this ).dialog( "close" );
                }
            }
        }],
        open: function() {
            $(".validateTips").text('');
            $("#comment_input").val('');
        },
        close: function() {
            $("#comment_input").removeClass( "ui-state-error" );
        }
    });
}
function initialize_filelist() {
	
    $.tablesorter.addParser({ 
        id: 'percentbars', 
        is: function(s) { 
            return false; 
        }, 
        format: function(s) {
            re = s.match(new RegExp(/(\d*%)/g));
            if (re) {
                s = re[0];
            }
            return $.tablesorter.formatFloat(s.replace(new RegExp(/%/g),""));
        }, 
        type: 'numeric' 
    });
    $.tablesorter.addParser({ 
        id: 'sortext', 
        is: function(s) { 
            return false; 
        }, 
        format: function(s) {
            re = s.match(new RegExp(/<sortext>(.+)<\/sortext>/));
            if (re) {
                s = re[1].toLowerCase();    
            } else {
                s = "";
            }
            return s;
        }, 
        type: 'text' 
    });

    $("#component_list").find('input').change(function(){
        var cfilter = [];
        $("#component_list").find('input:checked').each(function() {
            cfilter.push($(this).attr('id').substring(4));
        });
        check_filter_button();
        if (cfilter.length == 0) {
            show_ok_dialog(gettext("You can't hide all components."));
        } else {
            $.cookie("cmpfilter_"+LIST_PROJECT_RELEASE, cfilter.join(), { raw: true, expires: 30, path: '/' });
            if ($(this).is(':checked')) {
                $(this).next().children('.ui-button-icon-primary').addClass("ui-icon-circle-check").removeClass("ui-icon-circle-plus");
                load_component($(this).val());
            } else {
                $(this).next().children('.ui-button-icon-primary').addClass("ui-icon-circle-plus").removeClass("ui-icon-circle-check");
                hide_component($(this).attr('name'));
            }
        }
    });

    $("#filestabs").find('table').tablesorter({
        widgets: ['cookie'],
        sortList: [[0,0]]
    });
    
    $("#filestabs").find('table').bind("sortStart",function() { 
        loading(true);
    }).bind("sortEnd",function() { 
        loading(false);
    }); 
        
    jQuery.aop.before({target: jQuery.fn, method: "hide"},
    function(){
        this.trigger("hide");
    });
    
    $(document).keyup(function(event){
        if (event.keyCode == 27) {
            check_current();
        }
    });
    
    init_select_events();
		
    $("#filterbutton").click(function() {
        $("input[name='extraFunc']").each(function() {
            if ($(this).is(':checked')) {
                $.cookie($(this).attr('alt'), 'true', { expires: 30, path: '/' });
            } else {
                $.cookie($(this).attr('alt'), null, {path: '/' });
            }
        });			
        load_component(RELOAD_LIST_FILES_URL, true);
    });

    init_filedialogs()
		
} 
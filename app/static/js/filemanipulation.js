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
	$(div).bind("hide",function(){
		$(div).unbind("submit");
	});	
}

function select_user(elem, callback, param) {
    var topOffset = -10;
    //var leftOffset = $(elem).parent().width() * -1;
    var leftOffset = 10;

    var div = $('#user-selection-list');
    $(div).hide();
    $(div).submit(function(){
		$(this).hide();
		callback(param,{userid:$('#user-select').val()});
	});
	
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
			show_file_dialog(m.text());
		}
		var c = $(this).find('content');
		var id = $(this).find('id');
		if (c.length>0) {
			$("#file_row_"+id.text()).html(c.text());
		}
	});	
}

var current_id = false;

function check_current() {
	if (current_id) {
		$('#lock_comment_'+current_id).hide()
		$('#lock_break_'+current_id).show();
		$('#comment_'+current_id).unbind('keypress');
	}
}
function add_comment(id) {
	check_current();
	current_id = id;
	$('#lock_break_'+id).hide();
	$('#lock_comment_'+id).show()
	field = $('#comment_'+id)
	field.keypress(function (e) {
		if (e.which == 13) {
			$(this).unbind('keypress');
			$("#submit_"+id).click();
		}
	});
	field.focus()
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
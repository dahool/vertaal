function try_toggle_detail(url, opc) {
	data = {}
	if (opc!=undefined) {
		data = opc
	}
	check_current();
	$.post(url,
		  data,
		  process_toggle_response_detail,
		  "xml");
}
function try_toggle_detail_cnf(url, opc) {
	confirmSimple(function(r){
		if (r) {
			try_toggle_detail(url, opc);
		}
	});
}
function process_toggle_response_detail(data) {
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
		var id = $(this).find('id');
		if (c.length>0) {
			$("#details-assignblock").html(c.text());
		}
	});	
}

$(document).ready(function(){ 
	var icon_open = 'ui-icon-circle-triangle-s';
	var icon_closed = 'ui-icon-circle-triangle-w';
	$("#log-file-table").on('click', 'div.pagination a', function(ev) {
		ev.preventDefault();
		var url = $(this).attr('href');
		$("#log-file-table").load(url + " #log-file-table");
	})
	$(".collapsible").each(function() {
		$(this).find("caption").on('click', function() {
			var sp = $(this).find('span.ui-icon');
			if ($(sp).hasClass(icon_closed)) {
				$(sp).removeClass(icon_closed);
				$(sp).addClass(icon_open);
				$(this).parent().find('thead,tbody').show();
			} else {
				$(sp).removeClass(icon_open);
				$(sp).addClass(icon_closed);
				$(this).parent().find('thead,tbody').hide();			
			}
		}).append('<span class="ui-icon '+icon_closed+'"></span>');
		$(this).find("thead,tbody").hide();
	});
	init_select_events();
	init_filedialogs();
})

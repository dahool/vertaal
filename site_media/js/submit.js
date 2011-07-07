
function process(url) {
	data = $("input[name='file']").serialize();
	$.post(url,
			data,
			process_submit_response,
			"xml");
}

function show_submit_dialog(msg) {
	show_ok_dialog(msg);
}

function process_submit_response(data) {
	$(data).find('response').each(function(){
		var m = $(this).find('message');
		if (m.length>0) {
			show_submit_dialog(m.text());
		}
		var c = $(this).find('content');
		if (c.length>0) {
			$("#submit_table").html(c.text());
		}
	});	
}
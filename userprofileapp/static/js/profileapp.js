function createPagination() {
	var maxPages = 10;
	if ($(".jp-current").length == 0) {
		$("#trans_table_pages").jPages({
	        containerID  : "trans_table",
	        perPage      : maxPages,
	        previous: gettext("previous"),
	        next: gettext("next"),
		});
		$("#rev_table_pages").jPages({
	        containerID  : "rev_table",
	        perPage      : maxPages,
	        previous: gettext("previous"),
	        next: gettext("next"),
		});				
		$("#sub_table_pages").jPages({
	        containerID  : "sub_table",
	        perPage      : maxPages,
	        previous: gettext("previous"),
	        next: gettext("next"),
		});
		$("#lock_table_pages").jPages({
	        containerID  : "lock_table",
	        perPage      : maxPages,
	        previous: gettext("previous"),
	        next: gettext("next"),
		});						
	}
}
function remove_pro_fav(id) {
	$.post(url_profile_remove_fav,
			{id: id},
			process_remove_pro_fav_response,
			  "xml");	
}
function process_remove_pro_fav_response(data) {
	$(data).find('response').each(function(){
		var c = $(this).find('id');
		if (c.length>0) {
			$("#fav_"+c.text()).remove();
			$("#bookmark_"+c.text()).remove();
		}
	});	
}
function startup_set(id, remove) {
	if (remove == undefined) {
		url = url_add_startup;
		proc = process_set_startup;
	} else {
		url = url_remove_startup;
		proc = process_remove_startup;
	}
	$.post(url,
			{id: id},
			proc,
			  "xml");	
}
function process_remove_startup(data) {
	$(data).find('response').each(function(){
		var c = $(this).find('id');
		if (c.length>0) {
			$("#start_del_"+c.text()).hide();
			$("#start_set_"+c.text()).show();
		}
	});	
}
function process_set_startup(data) {
	$(data).find('response').each(function(){
		var c = $(this).find('id');
		if (c.length>0) {
			$("#start_del_"+c.text()).show();
			$("#start_set_"+c.text()).hide();
		}
	});	
}

$(document).ready(function(){
	$( "#tabs" ).tabs({
		active: ($.cookie('profile_tab') || 0),
		create: function(event, ui) {
			createPagination();
		},
		activate: function(event, ui) {
			$.cookie('profile_tab', ui.newTab.index());
			createPagination();
		}
	});	
});

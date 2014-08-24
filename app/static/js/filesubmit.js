$(document).ready(function(){ 

	$("#submitConfirmFileListDialog").on('click', 'div.pagination a', function(ev) {
		ev.preventDefault();
		var url = $(this).attr('href');
		$("#submit_table_files_container").load(url + " #submit_table_files_container");
	})

	$("#aShowMore").on('click', function(ev) {
		ev.preventDefault();
		var url = $(this).attr('href');
		$("#submitConfirmFileListDialog").html("");
		$("#submitConfirmFileListDialog").dialog("option", "title", gettext("File list")).dialog("open");
		$("#submitConfirmFileListDialog").load(url + " #submit_table_files_container");
	})
	
		
    $( "#submitConfirmFileListDialog" ).dialog({
        autoOpen: false,
        width: 600,
        modal: true,
        resizable: true,
        closeOnEscape: true,
        buttons: [{
        	text: _OK,
        	click : function() {
        		$( this ).dialog( "close" );
            }
        }],
    });
    
})

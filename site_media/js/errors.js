$(document).ready(function() {
	applyErrorSelector();
});

function applyErrorSelector() {
	$(".field-error").tooltip({className:'error-tip'});
}
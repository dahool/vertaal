
function popupoverlay(message) {
	$("BODY").append('<div id="popup_overlay"></div>');
	$("#popup_overlay").css({
		position: 'absolute',
		zIndex: 99998,
		top: '0px',
		left: '0px',
		width: '100%',
		height: $(document).height(),
		background: '#FFF',
		opacity: .5
	});	
}
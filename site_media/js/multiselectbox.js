/**
 * multiselectbox.js
 * A jquery multiselect replacement plugin
 * Copyright (c) 2009 SGT Dev.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * View the GNU General Public License <http://www.gnu.org/licenses/>.
 *
 * @author Sergio Gabriel Teves (info at sgtdev.com.ar)
 * @date 04/30/2009
 * @version 1.0.1
 * 
 * @requires jquery.js (tested with 1.3.2)
 * 
*/

(function($) {
	$.fn.multiselectbox = function(o){

		function get_field_html(id, name, value) {
			return '<input type="hidden" id="'+id+'_field" value="'+value+'" name="'+name+'"/>';
		}		
		function add_field(id, name, value, to) {
			$(to).append(get_field_html(id,name,value));
		}
		function remove_field(id) {
			$('#'+id+'_field').remove();
		}
		
		$(this).each(function() {
			var html = "";
			var fields = "";
			$(this).find("select").each(function() {
				var select = $(this);
				html += '<div class="w-combo-list" id="'+ $(select).attr('id') +'">';
				html += '<div class="w-combo-list-inner">';
				$(select).children().each(function() {
					var opt = $(this);
					var elid = $(select).attr('id')+"_opt_"+$(opt).val();
					var cls = 'w-combo-list-item .w-unselectable';
					if ($(opt).attr('selected')) {
						cls += ' w-combo-selected';
						fields += get_field_html(elid,$(select).attr('name'),$(opt).val());
					}
					html += '<div alt="'+ $(select).attr('name') +'" id="'+ elid +'" value="'+ $(opt).val() +'" class="'+ cls +'">'+ $(opt).text() +'</div>';
				}); // END CHILDREN
				html += '</div></div>';
			}); // END SELECT
			$(this).html(html);
			$(this).append(fields);

			$(this).find(".w-combo-list-item").each(function() {
				$(this).click(function() {
					if ($(this).hasClass('w-combo-selected')) {
						$(this).removeClass("w-combo-selected");
						remove_field($(this).attr('id'));
					} else {
						$(this).addClass("w-combo-selected");
						add_field($(this).attr('id'),$(this).attr('alt'),$(this).attr('value'),$(this).parent().parent().parent());
					}
				})
			});
						
		}); // END
	}
})(jQuery);
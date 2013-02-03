/**
 * simpletooltip2.js
 * Simple Tooltip
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
 * @date 05/02/2009
 * @revision 02/03/2013
 * @version 2.0.1
 * 
 * @requires jquery.js (tested with 1.8.2)
 * 
*/

( function( $ ) {
   $.fn.tooltip = function( o, callback ) {
       o = $.extend( { 
           className: null,
       }, o || {});
    
       var topOffset = -10;
       var leftOffset = 10;
       var maxWidth = 502; // px
       
       $(this).hover(
		      function (ev) {
		          var text = $(this).attr('title')
		          var div = '<div class="tooltipbox '+o.className+'" style="position: absolute; display: none;">';
		          div += '<div class="tip-wrap"><div class="tip-body">';
		          div += text;
		          div += '</div></div></div>';
		    	  $(this).append(div);
				  var tooltip = $(this).find("div." + o.className);
				  var p = $(this).position();
				  var w = tooltip.width();
				  if (w > maxWidth) w = maxWidth;
				  tooltip.css("top",(p.top+topOffset)+"px");
				  tooltip.css("left",(p.left+leftOffset)+"px");
				  tooltip.show();
				  tooltip.css("width",w);
		      }, 
		      function () {
		    	  $(this).find("div." + o.className).remove();
		      }
       );

   }
})( jQuery );
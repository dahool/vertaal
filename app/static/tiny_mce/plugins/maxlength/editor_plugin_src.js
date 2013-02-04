(function() {
	tinymce.create('tinymce.plugins.MaxLength', {
		/**
		 * Initializes the plugin, this will be executed after the plugin has been created.
		 * This call is done before the editor instance has finished it's initialization so use the onInit event
		 * of the editor instance to intercept that event.
		 *
		 * @param {tinymce.Editor} ed Editor instance that the plugin is initialized in.
		 * @param {string} url Absolute URL to where the plugin is located.
		 */
		init : function(ed, url) {
		    
			 function getMaxLength(ed) {
				max = ed.getParam("maxlength_"+ed.id, false);
				if (max==false) {
					max = ed.getParam("maxlength_value_all", false);
				}
	            return max;
	        };
			 
		    function controlLength(ed,e) {
		    	content = ed.getContent({format : 'raw'});
		    	maxL = getMaxLength(ed);
				if (e.keyCode == 0 && maxL) {
					len = content.replace(/(<([^>]+)>)/ig, "").replace(/&nbsp;/ig," ").length;
					if (len>=maxL) {
						e.stopPropagation();
						e.preventDefault();
					}
				}
            };
            
			ed.onKeyPress.add(controlLength);
		},


		/**
		 * Creates control instances based in the incomming name. This method is normally not
		 * needed since the addButton method of the tinymce.Editor class is a more easy way of adding buttons
		 * but you sometimes need to create more complex controls like listboxes, split buttons etc then this
		 * method can be used to create those.
		 *
		 * @param {String} n Name of the control to create.
		 * @param {tinymce.ControlManager} cm Control manager to use inorder to create new control.
		 * @return {tinymce.ui.Control} New control instance or null if no control was created.
		 */
		createControl : function(n, cm) {
			return null;
		},

		/**
		 * Returns information about the plugin as a name/value array.
		 * The current keys are longname, author, authorurl, infourl and version.
		 *
		 * @return {Object} Name/value array containing information about the plugin.
		 */
		getInfo : function() {
			return {
				longname : 'MaxLength plugin',
				author : 'Sergio Gabriel Teves',
				authorurl : '---',
				infourl : '---',
				version : "1.1"
			};
		}
	});

	// Register plugin
	tinymce.PluginManager.add('maxlength', tinymce.plugins.MaxLength);
})();
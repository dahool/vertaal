(function(){tinymce.create('tinymce.plugins.MaxLength',{init:function(ed,url){function getMaxLength(ed){max=ed.getParam("maxlength_"+ed.id,false);if(max==false){max=ed.getParam("maxlength_value_all",false)}return max};function controlLength(ed,e){content=ed.getContent({format:'raw'});maxL=getMaxLength(ed);if(maxL){len=content.replace(/(<([^>]+)>)/ig,"").replace(/&nbsp;/ig," ").length;if(len>=maxL){e.stopPropagation();e.preventDefault()}}};ed.onKeyPress.add(controlLength)},createControl:function(n,cm){return null},getInfo:function(){return{longname:'MaxLength plugin',author:'Sergio Gabriel Teves',authorurl:'---',infourl:'---',version:"1.0"}}});tinymce.PluginManager.add('maxlength',tinymce.plugins.MaxLength)})();
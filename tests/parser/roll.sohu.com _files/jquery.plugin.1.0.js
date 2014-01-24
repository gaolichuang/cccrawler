/**
 * @author qianwang
 * @modify 2011.3.14
 */
(function($){
	$.Buffer = new Array();
	$.Buffer.getBuffer = function(){
		var str = $.Buffer.join('');
		$.Buffer.length = 0;
		return str;
	};
	$.getBuffer = function(){
		var str = $.Buffer.join('');
		$.Buffer.length = 0;
		return str;
	};
	
	$.Buffers = function(){
		this._s = new Array;
	};
	$.Buffers.prototype = {
		append: function(str){
			this._s.push(str);
		},
		toString: function(){
			var str = this._s.join("");
			this._s.length = 0;
			return str;
		}
	};
	
	$.cookie = function(key, value, options){
		// key and at least value given, set cookie...    
		if (arguments.length > 1 && String(value) !== "[object Object]") {
			options = jQuery.extend({}, options);
			if (value === null || value === undefined) {
				options.expires = -1;
			}
			if (typeof options.expires === 'number') {
				var days = options.expires, t = options.expires = new Date();
				t.setDate(t.getDate() + days);
			}
			value = String(value);
			return (document.cookie = [
				encodeURIComponent(key), '=',
				options.raw ? value : encodeURIComponent(value),
				options.expires ? '; expires=' + options.expires.toUTCString() : '', // use expires attribute, max-age is not supported by IE            
	 			options.path ? '; path=' + options.path : '',
				options.domain ? '; domain=' + options.domain : '',
				options.secure ? '; secure' : ''
			].join(''));
		}
		// key and possibly options given, get cookie...    
		options = value || {};
		var result, decode = options.raw ? function(s){
			return s;
		} : decodeURIComponent;
		return (result = new RegExp('(?:^|; )' + encodeURIComponent(key) + '=([^;]*)').exec(document.cookie)) ? decode(result[1]) : null;
	};
	
	$.getScript = function(url, callback, cache, arg){
		$.ajax({
			type: "GET",
			url: url,
			success: function(){
				try {
					callback.apply(this, (arg || []));
				} catch (e) {
				}
			},
			dataType: "script",
			cache: cache
		});
	};
	
	$.getParm = function(u, o){
		var url = u ? u : window.location.toString();
		var tmp;
		if (url && url.indexOf("?")) {
			var arr = url.split("?");
			var parms = arr[1];
			var params = {};
			if (parms && parms.indexOf("&")) {
				var parmList = parms.split("&");
				jQuery.each(parmList, function(key, val){
					if (val && val.indexOf("=")) {
						var parmarr = val.split("=");
						if (o) {
							if (typeof(o) == "string" && o == parmarr[0]) {
								tmp = parmarr[1] == null ? '' : parmarr[1];
								return tmp;
							}
						} else {
							params[parmarr[0]] = parmarr[1];
						}
					}
				});
			}
		}
		return params;
	};
})(jQuery);

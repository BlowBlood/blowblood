(function() {

var xmlHttp;

function getXmlHttpObject() {
	var xmlHttp = null;
	try {
		xmlHttp = new XMLHttpRequest();
	} catch(e) {
		try {
			xmlHttp = new ActiveXObject("Msxml2.XMLHTTP");
		} catch(e) {
			xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
		}
	}
	return xmlHttp;
}

function page(wpurl, args, start, loading) {
	xmlHttp = getXmlHttpObject();
	if (xmlHttp == null) {
		alert ("Oop! Browser does not support HTTP Request.")
		return;
	}

	var url = wpurl;
	url += "?action=rc_ajax";
	url += "&args=" + args;
	url += "&start=" + start;

	xmlHttp.onreadystatechange = function(){runChange(loading)};
	xmlHttp.open("GET", url, true);
	xmlHttp.send(null);
}

function detail(id, wpurl, args, start, loading) {
	xmlHttp = getXmlHttpObject();
	if (xmlHttp == null) {
		alert ("Oop! Browser does not support HTTP Request.")
		return;
	}

	var url = wpurl;
	url += "?action=rc_detail_ajax";
	url += "&id=" + id;
	url += "&args=" + args;
	url += "&start=" + start;

	xmlHttp.onreadystatechange = function(){runChange(loading)};
	xmlHttp.open("GET", url, true);
	xmlHttp.send(null);
}

function runChange(loading) {
	var firstItem = document.getElementById("rc_item_1");
	var parent = firstItem.parentNode;
	var navigator = document.getElementById("rc_nav");

	if (xmlHttp.readyState < 4) {
		document.body.style.cursor = 'wait';
		if (navigator) {
			navigator.innerHTML = (loading == undefined) ? "Loading..." : loading + "...";
		}

	} else if (xmlHttp.readyState == 4 || xmlHttp.readyState=="complete") {
		parent.innerHTML = xmlHttp.responseText;
		document.body.style.cursor = 'auto';
	}
}

window['RCJS'] = {};
window['RCJS']['page'] = page;
window['RCJS']['detail'] = detail;

})();

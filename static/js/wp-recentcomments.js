(function() {
var xmlHttp;
var prevcontent;
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
function detail(wpurl, id, args, loading) {
	xmlHttp = getXmlHttpObject();
	if (xmlHttp == null) {
		alert ("Oop! Browser does not support HTTP Request.")
		return;
	}
	var url = wpurl;	
	url += "&amp;id=" + id;
	url += "&amp;args=" + args;
	
	xmlHttp.onreadystatechange = function(){runChange(loading)};
	xmlHttp.open("GET", url, true);
	xmlHttp.send(null);
}
function runChange(loading) {
	var parent = document.getElementById("rc_comm_list");
	var navigator = document.getElementById("rc_nav");
	prevcontent = parent.innerHTML

	if (xmlHttp.readyState < 4) {
		document.body.style.cursor = 'wait';
		if (navigator) {
			navigator.innerHTML = (loading == undefined) ? "Loading..." : loading + "...";
		}

	} else if (xmlHttp.readyState == 4 && xmlHttp.status == 200 ) {	  
		parent.innerHTML = xmlHttp.responseText;
		document.body.style.cursor = 'auto';
	}
}
function goback(){
  var parent = document.getElementById("rc_comm_list");
	parent.innerHTML = prevcontent;
	document.getElementById("rc_nav").innerHTML="<br />"
}
window['RCJS'] = {};
window['RCJS']['detail'] = detail;
window['RCJS']['goback'] = goback;
})();

function toggle(){
    var content = document.getElementById('Toggle');
    if (content.innerHTML  == 'Hide'){
    content.innerHTML = 'Show';
     	    document.getElementById("main").style.width = "960px";
         document.getElementById("sidebar").style.display = "none"; 
    }else{ 
         content.innerHTML = 'Hide';
          	    document.getElementById("main").style.width = "700px";
        document.getElementById("sidebar").style.display = "block"; 	
   }
}
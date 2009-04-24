String.prototype.trim = function () {
    return this.replace(/^[\s\,]*/, "").replace(/[\s\,]*$/, ""); //for remove the space and comma at the begining/end of the tag.
};
    
function parseBlogContent(){
  var title_input = document.forms["addblog"]["title_input"];
  var tags = document.forms["addblog"]["tags"];
  tags.value = tags.value.trim();
  if(title_input.value==""){
     alert("Please input title of the item.");
     title_input.focus();
     return false;
  }
  if(tags.value.indexOf(" ")!=-1){
     alert("Please remove the space or replace it with '_' in the tags.");
     tags.focus();
     return false;
  }
};
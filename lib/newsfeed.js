$(document).ready(function(){
  $("#create-group-btn").click(function (){
    $("#create-group-btn").fadeOut(200, function(){
      $("#btn-container").append("<form id='create-group-form' method='POST' action='create_group'> </form>");
      $("#create-group-form").append("<input class='text-area' id='group-name-text' type='text' name='group_name' value='Group Name'>");
      $("#create-group-form").append("<select class='text-area' name='type'> <option value='public'> Public </option> <option value='private'> Private </option> </select>");
      $("#create-group-form").append("<input class='text-area' id='group-name-description' type='text' name='description' value='description'>");
      $("#create-group-form").append("<input class='text-area' type='submit' value='submit'>");
      $("#btn-container").animate({"backgroundColor" : "teal", "padding" : "3vh"})
      $("#group-name-text").click(function(){
        $("#group-name-text").attr("value", "")
      });
      $("#group-name-description").click(function(){
        $("#group-name-description").attr("value", "")
      });
    });
  });
  // $("#btn-container").mouseleave(function() {
  //   $("#btn-container").remove();
  //   $("#create-group-btn").css({"display" : "block"})
  // });
});

// $(document).ready(function(){
//   $("#create-group-btn").click(function (){
//     $("#create-group-btn").fadeOut(100, function(){
//       $("#btn-container").append("<form id='create-group-form' method='POST' action='create_group'> </form>");
//       $("#create-group-form").append("<input class='text-area' id='group-name-text' type='text' name='group_name' value='Group Name'>");
//       $("#create-group-form").append("<select class='text-area' name='type'> <option value='public'> Public </option> <option value='private'> Private </option> </select>");
//       $("#create-group-form").append("<textarea class='text-area' id='group-name-description' type='textarea' name='description' value='description'>");
//       $("#create-group-form").append("<input class='text-area' id='text-area-submit' type='submit' value='submit'>");
//       $("#btn-container").animate({"backgroundColor" : "teal", "padding" : "3vh"})
//       $("#group-name-text").click(function(){
//         $("#group-name-text").attr("value", "")
//       });
//       $("#group-name-description").click(function(){
//         $("#group-name-description").attr("value", "")
//       });
//     });
//   });

$(document).ready(function(){
  $("#create-group-btn").click(function (){
    $("#create-group-btn").fadeOut(100, function(){
      $("#btn-container").append("<form id='create-group-form' method='POST' action='create_group'> </form>");
      $("#create-group-form").append("<input class='text-area' id='group-name-text' type='text' name='group_name' value='Group Name'>");
      $("#create-group-form").append("<select class='text-area' name='type'> <option value='public'> Public </option> <option value='private'> Private </option> </select>");
      $("#create-group-form").append("<textarea class='text-area' id='group-name-description' type='textarea' name='description' value='description'>");
      $("#create-group-form").append("<input class='text-area' id='text-area-submit' type='submit' value='submit'>");
      $("#btn-container").animate({"backgroundColor" : "#80CBC4", "padding" : "3vh"})
      $("#group-name-text").click(function(){
        $("#group-name-text").attr("value", "")
      });
      $("#group-name-description").click(function(){
        $("#group-name-description").attr("value", "")
      });
    });
  });

  $("#change-view").click(function (){
    $(".info").remove();
    $(".newsfeed-groups").css({"float" : "left", "text-align" : "center", "marginRight" : "auto", "marginLeft" : "auto"})
    $(".newsfeed-groups").animate({"width" : "32vw", "paddingRight" : "2vw", "marginRight" : "2vw", "height": "75vh"}, 1000);
    $(".photogroup-pic").animate({"maxWidth" : "32vw", "maxHeight" : "50vh"}, 2000);
    $(".no-images").animate({"width" : "32vw", "marginTop" : "2vh"}, 2000);
  });


  $(".newsfeed-groups").mouseenter(function(){
    $(this).css({"boxShadow" : "0vh 0vh 2vh black"});
  });
  $(".newsfeed-groups").mouseleave(function(){
    $(this).css({"boxShadow" : ""});
  });


});

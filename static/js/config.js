var specUrl = '/api/swagger.json';
var swaggerClient = new SwaggerClient({url:specUrl,disableInterfaces: false});

function addRacingGroup(race_id) {
    swaggerClient.then(function(client) {
      console.log('client', client);
      client.apis.RacingGroups.post_racinggroups({'object':{'race_id':race_id}}).then(
              function(){location.reload(); return false;});
    });
}

//addParticipant model yacht filter
$(document).ready(function(){
  $("button#yachtClassButton").click(function() {
    var e=this;
    swaggerClient.then(function(client) {
      console.log('client', client);
      //turn it off
      if ($(e).attr('area-pressed') == "true") {
          client.apis.RacingGroups.api_racinggroups_removeYachtClass({'racinggroup_id':$(e).closest("div#configure-classes").attr('racinggroup-id'),'yachtclass_id':$(e).attr('data-id')});
          $(e).attr('area-pressed',"false");
          }
      //turn it on
      else {
          client.apis.RacingGroups.api_racinggroups_addYachtClass({'racinggroup_id':$(e).closest("div#configure-classes").attr('racinggroup-id'),'yachtclass_id':$(e).attr('data-id')});
          $(e).attr('area-pressed',"true");
      }
    });
  });

  $("#filterPilot").on("keyup", function() {
    var value = $(this).val().toLowerCase();
    $("#listPilots button").filter(function() {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
    });
  });

  $("#filterYacht").on("keyup", function() {
    var value = $(this).val().toLowerCase();
    $("#listYachts button").filter(function() {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
    });
  });

  $("#listPilots button.pilot").on("click", function() {
	$("form#addParticipant input#personId").val($(this).attr("data-id"));
	$("form#addParticipant input#inputFirstname4").val($(this).attr("data-firstname"));
	$("form#addParticipant input#inputLastname4").val($(this).attr("data-lastname"));
	$("form#addParticipant input#inputEmail4").val($(this).attr("data-email"));
  });

  $("#listYachts button.yacht").on("click", function() {
	$("form#addParticipant input#yachtId").val($(this).attr("data-id"));
	$("form#addParticipant input#inputSailnumber4").val($(this).text());
	$("form#addParticipant #inputClass.option[data-id=" + $(this).attr("data-yachtclass-id") +"]").attr("selected","selected");
  });

  $("form#addParticipant select#inputClass4").change(function() {
	$("form#addParticipant input#yachtClassId").val($(this).children("option:selected").attr("data-id"));
  });

  $("div#addParticipant button#save").on("click", function() {
        var racinggroup_id=$(this).attr("data-racinggroup-id");
        swaggerClient.then(function(client) {
          var json={};
          $.each($("form#addParticipant").serializeArray(),function(i,fields){
            //skip empty fields
            if (fields.value == ""){return;}
            //fields ending on _id are integer
            if(fields.name.indexOf("_id") > -1) 
            { json[fields.name]=parseInt(fields.value,10);}
            else { json[fields.name]=fields.value;}
          });
          console.log('addParticipant', json);
          console.log('client', client);
          client.apis.RacingGroups.api_racinggroups_addParticipant({'racinggroup_id':racinggroup_id,'object':json}).then(
                  function(){cleanForm();location.reload(); return false;});
        });
  });
  //unset personID if person part of form manually filled out
  $("form#addParticipant input.person").on("keyup", function() {
	$("form#addParticipant input#personId").val("");
  });
  //unset personID if person part of form manually filled out
  $("form#addParticipant input.yacht").on("keyup", function() {
	$("form#addParticipant input#yachtId").val("");
  });
});

function cleanForm() {
	$("form#addParticipant input#inputFirstname4").val("");
	$("form#addParticipant input#inputLastname4").val("");
	$("form#addParticipant input#inputEmail4").val("")
	$("form#addParticipant input#yachtId").val("")
	$("form#addParticipant input#inputSailnumber4").val("")
	$("form#addParticipant #inputClass.option").attr("selected","");
        return;
}

heatid=$("div#scoring").attr("heat-id")
var specUrl = '/api/swagger.json';
var swaggerClient = new SwaggerClient({url:specUrl,disableInterfaces: false});
loadScoringButtons();
loadRoundings();
var scoringLastPass=0

function loadScoringButtons() {
swaggerClient.then(function(client) {
  console.log('client', client);
  client.apis.Heats.api_heats_getParticipants({'heat_id':heatid})
    .then(function(participants) {
      var items = [];
      //sorted=participants.obj.sort(sortByPassingOrder);
      //for (i=0;i<sorted.length;i++){
        //items.push( "<button type='button' class='btn btn-secondary btn-rounding' participant-id='" + sorted[i].participant.id + "'>" + sorted[i].participant.yacht.sailnumber + " (" + sorted[i].position + ")</button>" );
      //}
      $.each( participants.obj.sort(sortByPassingOrder), function( key, obj ) {
	items.push( "<button type='button' class='btn btn-secondary btn-rounding' participant-id='" + obj.participant.id + "'>" + obj.participant.yacht.sailnumber + " (" + obj.position + ")</button>" );
      });
     
      $("div#scoringButtons").html("");
      $( "<ul/>", { "class": "my-new-list", html: items.join( "" ) }).appendTo( "div#scoringButtons" );

    $("button.btn-rounding").click(function(){
        participant_id = parseInt($(this).attr("participant-id"),10);
        //hide the button immediately for if the submission takes a while
        $(this).addClass('d-none')
        //Add the rounding to the grid immediately too
	$('div#roundingGrid table').append( "<td><div class='' participant-id='" + participant_id + "'>" + $(this).text() + "</div></td>" );
        //Submit the rounding
        swaggerClient.then(function(client) {
            client.apis.Heats.api_heats_addRounding({'heat_id':heatid,'object':{participant_id:participant_id,'mark_id':1}})
        //swaggerClient
            .then(function(){loadScoringButtons();loadRoundings()});
        });
    });

    })
    .catch(function(error) {
      console.log('Oops!  failed with message: ' + error.statusText);
    });
});
}

function loadRoundings(){
swaggerClient.then(function(client) {
  console.log('client', client);
  client.apis.Heats.api_heats_getRoundings({'heat_id':heatid})
    .then(function(roundings) {
      var items = [];
      var ids = [];//ids list to check if participant appears in row already. purpose is to have each lap on new line
      items.push("<tr>");
      $.each( roundings.obj, function( key, obj ) {
          if ( ids.includes(obj.participant_id)){
              ids.length=0; //flush the ids list
              items.push("</tr><tr>"); //make new row
          }
          ids.push(obj.participant_id);
        console.log('obj', obj);
        date=new Date(obj.overriddentime);
        items.push( "<td><div class='roundingGridItem' data-rounding-id='"+obj.id+"' data-overriddentime='"+obj.overriddentime+"' data-participant-id='" + obj.participant_id + "'>" + obj.participant.yacht.sailnumber + " (" + date.toLocaleTimeString() + ")</div></td>" );
      });
 
      items.push("</tr>");
      $("div#roundingGrid").html("");
      $( "<table/>", { "class": "table table-striped table-bordered table-sm", html: items.join( "" ) }).appendTo( "div#roundingGrid" );

      $(".roundingGridItem").click(function(){
      $('#updateRounding').attr('data-rounding-id',$(this).attr('data-rounding-id'));
      $('#updateRounding #inputOverriddenTime4').val($(this).attr('data-overriddentime'));
      $('#updateRounding #inputHeatId4').val($(this).attr('data-heat-id'));
      $('#updateRounding #inputParticipant4 option').removeAttr('selected');
      $('#updateRounding #inputParticipant4 option[data-id='+$(this).attr('data-participant-id')+']').attr('selected','selected');

      $('#updateRounding').modal('show')});
    });
});
}

//heat status update buttons
$(document).ready(function(){
  $("button#heatStatusButton").click(function() {
    var e=this;
    swaggerClient.then(function(client) {
      return client.apis.Heats.put_heats__object_id_({'object_id':parseInt($(e).attr("data-heat-id"),10),'object':{'status':parseInt($(e).attr('data-id'),10)}})
      })
      .then(function(){return location.reload()});
  });

    //updateRounding modal - save button
  $("#updateRounding button#save").on("click", function() {
        var rounding_id=$(this).attr("data-rounding-id");
        swaggerClient.then(function(client) {
          var json={};
          $.each($("form#updateRounding").serializeArray(),function(i,fields){
            //skip empty fields
            if (fields.value == ""){return;}
            //fields ending on _id are integer
            if(fields.name.indexOf("_id") > -1) 
            { json[fields.name]=parseInt(fields.value,10);}
            else { json[fields.name]=fields.value;}
          });
          console.log('updateRounding', json);
          console.log('client', client);
          client.apis.Roundings.put_roundings__object_id_({'object_id':parseInt($('#updateRounding').attr("data-rounding-id"),10),'object':json}).then(
                  function(){$('#updateRounding').modal('hide');loadRoundings(); return false;});
        });
  });

    //updateRounding modal - delete button
  $("#updateRounding button#delete").on("click", function() {
        var rounding_id=$(this).attr("data-rounding-id");
        swaggerClient.then(function(client) {
          client.apis.Roundings.delete_roundings__object_id_({'object_id':parseInt($('#updateRounding').attr("data-rounding-id"),10)}).then(
                  function(){$('#updateRounding').modal('hide');loadRoundings(); return false;});
        });
  });
    //updateRounding modal - sets the selected participant into hidden form field
    $("#updateRounding select#inputParticipant4").change(function() {
    $("#updateRounding input#participantId").val($(this).children("option:selected").attr("data-id"));
    });
});


function sortByPassingOrder(a, b){
      var aPassingOrder = a.passing_order;
      var bPassingOrder = b.passing_order;
      return ((aPassingOrder < bPassingOrder) ? -1 : ((aPassingOrder > bPassingOrder) ? 1 : 0));
}

function sortByLastPass(a, b){
      var aPassingOrder = a.passing_order;
      var bPassingOrder = b.passing_order;
      return ((aPassingOrder < bPassingOrder) ? -1 : ((aPassingOrder > bPassingOrder) ? 1 : 0));
}

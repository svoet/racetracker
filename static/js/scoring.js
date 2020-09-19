heatid=$("div#scoring").attr("heat-id")
var specUrl = '/api/swagger.json';
var swaggerClient = new SwaggerClient({url:specUrl,disableInterfaces: false});
loadScoringButtons();
loadRoundings();

function loadScoringButtons() {
swaggerClient.then(function(client) {
  console.log('client', client);
  client.apis.Heats.api_heats_getParticipants({'heat_id':heatid})
    .then(function(participants) {
      var items = [];
      $.each( participants.obj, function( key, obj ) {
	items.push( "<button type='button' class='btn btn-secondary btn-rounding' participant-id='" + obj.participant.id + "'>" + obj.participant.yacht.sailnumber + " (" + obj.position + ")</button>" );
      });
     
      $("div#scoringButtons").html("");
      $( "<ul/>", { "class": "my-new-list", html: items.join( "" ) }).appendTo( "div#scoringButtons" );

    $("button.btn-rounding").click(function(){
        participant_id = parseInt($(this).attr("participant-id"),10);
        swaggerClient.then(function(client) {
            client.apis.Heats.api_heats_addRounding({'heat_id':heatid,'object':{participant_id:participant_id,'mark_id':1}})
        swaggerClient
        loadScoringButtons();
        loadRoundings();
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
        date=new Date(obj.overriddentime);
	items.push( "<td><div class='' participant-id='" + obj.participant.id + "'>" + obj.participant.yacht.sailnumber + " (" + date.toLocaleTimeString() + ")</div></td>" );
      });
     
      items.push("</tr>");
      $("div#roundingGrid").html("");
      $( "<table/>", { "class": "table table-striped table-bordered table-sm", html: items.join( "" ) }).appendTo( "div#roundingGrid" );
    });
});
}


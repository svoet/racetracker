race_id=$("div#live").attr("race-id")
var specUrl = '/api/swagger.json';
var swaggerClient = new SwaggerClient({url:specUrl,disableInterfaces: false});
loadLive();
window.setInterval(function(){ loadLive() }, 5000);

function loadLive(){
swaggerClient.then(function(client) {
  console.log('client', client);
  client.apis.Races.get_races__object_id_({'object_id':race_id})
    .then(function(race) {
      console.log('race', race);
      $.each( race.obj.racinggroups, function( key, racinggroup ) {
        dom="div#liveRacingGroup" + racinggroup.id;
        if (!$(dom).length){
            $("div#live").append("<div id='liveRacingGroup" + racinggroup.id + "'>");
        }
        processRacingGroup(racinggroup,dom )
      });
     
    });
});
}

function processRacingGroup(racinggroup,dom){
      var items = [];
      var highest = 0;//ids list to check if participant appears in row already. purpose is to have each lap on new line
      $.each( racinggroup.heats, function( key, heat ) {
          if(heat.id > highest && (heat.status == 1 || heat.status == 2)){ highest = heat.id;}
      });

      swaggerClient.then(function(client) {
          client.apis.Heats.api_heats_getParticipants({'heat_id':highest})
            .then(function(participants) {
                participants.obj.sort(sortByPosition);
                $.each( participants.obj, function( key, obj ) {
                    items.push("<tr participant-id='" + obj.participant.id + "'>");
                    items.push( "<td>" + obj.position + "</td><td>" + obj.participant.yacht.sailnumber + "</td><td>" + obj.participant.person.firstname + " " + obj.participant.person.lastname + "</td><td>" + obj.roundings.length +  "</td>");
                    //items.push( "<td>" + participant.yacht.sailnumber + "</td><td>" + date.toLocaleTimeString() + ")</div></td>" );
                    items.push("</tr>");
                });

          $(dom).html("");
          $( "<div/>", { "class": "", html: racinggroup.name }).appendTo(dom);
          $( "<table/>", { "class": "table table-striped table-bordered table-sm", html: items.join( "" ) }).appendTo(dom);
            });
        });
};
function sortByStarttime(a, b){
      var aDate = new Date(a.starttime);
      var bDate = new Date(b.starttime);
      return ((aDate < bDate) ? -1 : ((aDate > bDate) ? 1 : 0));
}

function sortByPosition(a, b){
      var aPosition = a.position;
      var bPosition = b.position;
      return ((aPosition < bPosition) ? -1 : ((aPosition > bPosition) ? 1 : 0));
}

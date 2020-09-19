var specUrl = '/api/swagger.json';
var swaggerClient = new SwaggerClient({url:specUrl,disableInterfaces: false});

function addRacingGroup(race_id) {
    swaggerClient.then(function(client) {
      console.log('client', client);
      client.apis.RacingGroups.post_racinggroups({'object':{'race_id':race_id}}).then(
              function(){location.reload(); return false;});
    });
}

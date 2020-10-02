$(document).ready(function () {

    $("#sidebar").mCustomScrollbar({
         theme: "minimal"
    });

    $('#dismiss').on('click', function () {
            // hide sidebar
            $('#sidebar').toggleClass('active');
            $('#content').addClass('active');
        });

    $('#sidebarCollapse').on('click', function () {
        // open or close navbar
        $('#sidebar').toggleClass('active');
        $('#content').toggleClass('active');
        // fade in the overlay
        $('.overlay').addClass('active');
        // close dropdowns
        $('.collapse.in').toggleClass('in');
        // and also adjust aria-expanded attributes we use for the open/closed arrows
        // in our CSS
        $('a[aria-expanded=true]').attr('aria-expanded', 'false');
    });

    $('nav#sidebar a#addHeat').click(function(){
        var e=this;
        swaggerClient.then(function(client) {
          console.log('client', client);
          return client.apis.RacingGroups.api_racinggroups_addHeat({'racinggroup_id':$(e).attr("data-id"),'heat':{}}) ;
        }).then(function(){return location.reload()});
    });
});

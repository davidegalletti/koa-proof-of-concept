$( document ).ready(function() {
    var today = new Date();
    var m = 60 -today.getMinutes();
    document.getElementById('time').innerHTML = "This demo will be reset every hour. " + m + " minutes to go.";
    $(function() {
      $( document ).tooltip();
    });
}); 


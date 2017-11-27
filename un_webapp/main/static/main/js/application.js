$(document).ready(function() {
    $(document).on("click", ".save-content", function(e){
      e.preventDefault();
      $.ajax({
        type: 'GET',
        url: '/search/save-content/?user=' + user +"&content=" + this.dataset.pk,
        success: function(data) {
          alert(data['message']);
        }
      });
    });
});

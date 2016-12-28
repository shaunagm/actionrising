$(document).ready(function(){

  $('.share-popover').popover({
    html : true,
    content: function() {
      return $('#share_popover_content').html();
    }
  });

  $('.flag-popover').popover({
    html : true,
    content: function() {
      return $('#flag_popover_content').html();
    }
  });

  $('.manage-action-popover').popover({
    html : true,
    content: function() {
      return $('#manage_action_popover_content').html();
    }
  });

  $('.manage-slate-popover').popover({
    html : true,
    content: function() {
      return $('#manage_slate_popover_content').html();
    }
  });

});

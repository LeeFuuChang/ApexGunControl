(function(){
    $(".app-control-button").on("click", function(){
        $.post(`/app/controls/${$(this).attr("name")}`);
    });
})();
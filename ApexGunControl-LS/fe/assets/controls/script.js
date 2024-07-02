(function(){
    $(".app-control-button[name='app-control-close']").on("click", ()=>{
        $.post("/app/controls/app-control-close");
    });
    $(".app-control-button[name='app-control-minimize']").on("click", ()=>{
        $.post("/app/controls/app-control-minimize");
    });
    $(".app-control-button[name='app-control-settings']").on("click", ()=>{
        window.LoadOverlay("info");
    });
})();
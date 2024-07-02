window.LoadOverlay = function(name) {
    $("#overlay").css("display", "grid");
    $("#overlay-container").attr("name", name);
    $.get(`assets/overlay/${name}/overlay.html`, {}, (html)=>{
        $(html).appendTo($("#overlay-container").empty());
        window.LoadLang();
    });
};

window.HideOverlay = function() {
    $("#overlay").css("display", "none");
    $("#overlay-container").empty();
};

(function(){
    $("#overlay").on("click", function(e){
        if(this == e.target) window.HideOverlay();
    });
})();
window.Notify = function(type, message) {
    var element = $(`
        <div class="notify notify-${type}">
            <strong>${type[0].toUpperCase()+type.slice(1)}</strong> ${message}
        </div>
    `);
    element.appendTo($("#notify-container"));
    setTimeout(()=>{
        element.fadeOut(1500, function() { $(this).remove(); });
    }, 1500);
};


window.Resize = function(scale) {
    $(":root").css("--scale", scale);
    $.post(
        "/app/controls/app-control-resize", 
        JSON.stringify([
            $("html")[0].getBoundingClientRect().width,
            $("html")[0].getBoundingClientRect().height,
        ])
    );
};


window.LoadPage = function(name) {
    if(firebase.auth().currentUser || name === "dashboard") {
        $("#page").attr("name", name).empty();
        $("nav .side-button, nav .main-nav-button").removeClass("active");
        $(`nav .side-button[name="${name}"], nav .main-nav-button[name="${name}"]`).addClass("active");
        $.get(`assets/main/pages/${name}/page.html`, {}, (html)=>{
            $(html)
                .hide()
                .appendTo($("#page"))
                .fadeIn(250);
            window.LoadLang();
        });
    }
    else {
        window.LoadOverlay("login");
    }
};
window.RefreshPage = function() {
    window.LoadPage($("#page").attr("name"));
};
window.LoadHomePage = function() {
    window.LoadPage("dashboard");
};


window.LoadOverlay = function(name) {
    $("#overlay").css("display", "grid");
    $("#overlay-container").attr("name", name);
    $.get(`assets/overlay/${name}/overlay.html`, {}, (html)=>{
        $("#overlay-container")
            .hide()
            .empty()
            .append($(html))
            .fadeIn(250, function(){
                $(this).find("[tabindex='0']").focus()
            });
        window.LoadLang();
    });
};
window.HideOverlay = function() {
    $("#overlay").css("display", "none");
    $("#overlay-container").empty();
};


window.LoadLang = function() {
    $(".lang").each(function(){
        $(this).text(window.GetLangText($(this).attr("lang")))
    });
};


$(window).on("focus", window.RefreshPage);


$(document).ready(function(){
    /*
    Initialization
    */
    $.get("/app/config/app.json", {})
        .then((config)=>{
            window.SetLanguage(config["language"]);
            window.Resize(parseFloat(config["window-scale"]) || 1);
        });


    /*
    Navigation
    */
    $("nav .side-button").on("click", function(){
        if(!$(this).attr("name")) return;
        window.LoadPage($(this).attr("name"));
    });
    $("nav .main-nav-button").on("click", function(){
        window.LoadPage($(this).attr("name"));
    });


    /*
    Overlay
    */
    $("#overlay").on("click", function(e){
        if(this == e.target) window.HideOverlay();
    });


    /*
    Controls
    */
    $(".app-control-button[name='app-control-close']").on("click", ()=>{
        $.post("/app/controls/app-control-close");
    });
    $(".app-control-button[name='app-control-minimize']").on("click", ()=>{
        $.post("/app/controls/app-control-minimize");
    });
    $(".app-control-button[name='app-control-settings']").on("click", ()=>{
        window.LoadOverlay("info");
    });


    /*
    Landing
    */
    window.LoadHomePage();
    window.LoadOverlay("login");
});
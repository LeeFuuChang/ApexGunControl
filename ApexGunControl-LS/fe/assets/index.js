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
            $(html).appendTo($("#page"));
            window.LoadLang();
        });
    }
    else {
        window.LoadOverlay("login");
    }
};
window.ReloadPage = function() {
    window.LoadPage($("#page").attr("name"));
};
window.LoadHomePage = function() {
    window.LoadPage("dashboard");
};


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


window.LoadLang = function() {
    let lang = $("#app").attr("lang") || "en";
    $(".lang").each(function(){
        $(this).text(window.translation[$(this).attr("lang")][lang]);
    });
};


window.weaponData = [{
    name: "R-301",
    ammo: "Light",
    type: "repeat",
    assisting: true,
    multiplier: 1,
    usage: 147243,
    image: "assets/media/weapons/R-301.png",
}, {
    name: "L-STAR EMG",
    ammo: "Energy",
    type: "repeat",
    assisting: true,
    multiplier: 1,
    usage: 147243,
    image: "assets/media/weapons/L-STAR.png",
}, {
    name: "Flatline",
    ammo: "Heavy",
    type: "repeat",
    assisting: true,
    multiplier: 1,
    usage: 147243,
    image: "assets/media/weapons/Flatline.png",
}, {
    name: "R-99",
    ammo: "Light",
    type: "repeat",
    assisting: true,
    multiplier: 1,
    usage: 147243,
    image: "assets/media/weapons/R-99.png",
}, {
    name: "Volt SMG",
    ammo: "Energy",
    type: "repeat",
    assisting: true,
    multiplier: 1,
    usage: 147243,
    image: "assets/media/weapons/Volt.png",
}];


$(document).ready(function(){
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
    Main
    */
    window.LoadHomePage();
});
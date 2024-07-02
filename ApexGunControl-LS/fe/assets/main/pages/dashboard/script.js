(function(){
    if(firebase.auth().currentUser) {
        $("#page[name='dashboard'] .auth .state p")
            .text(window.translation["page-dashboard-state-unauthorized"][$("#app").attr("lang")||"en"]);
        $("#page[name='dashboard'] .auth input")
            .removeAttr("disabled")
            .attr("placeholder", window.translation["page-dashboard-placeholder-input"][$("#app").attr("lang")||"en"]);
        $("#page[name='dashboard'] .auth button")
            .text(window.translation["page-dashboard-button-submit"][$("#app").attr("lang")||"en"])
            .off("click")
            .on("click", ()=>{
                console.log("submit")
            });
    }
    else {
        $("#page[name='dashboard'] .auth .state p")
            .text(window.translation["page-dashboard-state-waiting"][$("#app").attr("lang")||"en"]);
        $("#page[name='dashboard'] .auth input")
            .attr("disabled", "disabled")
            .attr("placeholder", window.translation["page-dashboard-placeholder-waiting"][$("#app").attr("lang")||"en"]);
        $("#page[name='dashboard'] .auth button")
            .text(window.translation["page-dashboard-button-login"][$("#app").attr("lang")||"en"])
            .off("click")
            .on("click", ()=>{
                window.LoadOverlay("login");
            });
    }


    window.LoadLang();
})();
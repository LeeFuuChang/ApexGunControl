setTimeout(function(){
    if(window.auth().user) {
        $("#page[name='dashboard'] .auth .state p")
            .text(window.auth().authorized ? (
                window.auth().expireAt
            ) : (
                window.GetLangText("page-dashboard-state-unauthorized")
            ));
        $("#page[name='dashboard'] .auth input")
            .removeAttr("disabled")
            .attr("placeholder", window.GetLangText("page-dashboard-placeholder-input"));
        $("#page[name='dashboard'] .auth button")
            .text(window.GetLangText("page-dashboard-button-submit"))
            .off("click")
            .on("click", ()=>{
                let pin = $("#page[name='dashboard'] .auth input").val();
                if(pin) return window.auth().activate(pin);
                return window.Notify("error", window.GetLangText("page-dashboard-no-pin"));
            });
    }
    else {
        $("#page[name='dashboard'] .auth .state p")
            .text(window.GetLangText("page-dashboard-state-waiting"));
        $("#page[name='dashboard'] .auth input")
            .attr("disabled", "disabled")
            .attr("placeholder", window.GetLangText("page-dashboard-placeholder-waiting"));
        $("#page[name='dashboard'] .auth button")
            .text(window.GetLangText("page-dashboard-button-login"))
            .off("click")
            .on("click", ()=>{
                window.LoadOverlay("login");
            });
    }
}, 100);
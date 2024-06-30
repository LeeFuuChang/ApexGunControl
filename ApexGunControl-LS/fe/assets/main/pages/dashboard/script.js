(function(){
    if(firebase.auth().currentUser) {
        $("#page[name='dashboard'] .auth .state p")
            .text("UnAuthorized");
        $("#page[name='dashboard'] .auth input")
            .removeAttr("disabled")
            .attr("placeholder", "Credential Code");
        $("#page[name='dashboard'] .auth button")
            .text("Submit")
            .off("click")
            .on("click", ()=>{
                console.log("submit")
            });
    }
    else {
        $("#page[name='dashboard'] .auth .state p")
            .text("Waiting for Login");
        $("#page[name='dashboard'] .auth input")
            .attr("disabled", "disabled")
            .attr("placeholder", "Please Login first");
        $("#page[name='dashboard'] .auth button")
            .text("Login")
            .off("click")
            .on("click", ()=>{
                window.LoadOverlay("login");
            });
    }
})();
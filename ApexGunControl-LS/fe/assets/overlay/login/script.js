(function(){
    $.get("/app/config/user.json")
        .then((data)=>{
            $("#login-input").val(data["username"] || "");
        });
    $("#login-submit")
        .on("click", function(){
            let email = $("#login-input").val();
            if((/^\S+(\.\S+)*@\S+(\.\S+)+$/).test(email)) {
                $.post("/app/config/user.json", JSON.stringify({"username": email}));
                window.auth().login(email, email.split("@")[0])
                    .then(()=>{
                        if(window.auth().user) {
                            window.HideOverlay();
                        }
                    });
            }
            else {
                window.Notify("error", window.GetLangText("overlay-login-wrong-format"));
            }
        });
    $("#login-input")
        .focus()
        .keyup(function(e){
            if(e.keyCode == 13) $("#login-submit").trigger("click");
        });
})();
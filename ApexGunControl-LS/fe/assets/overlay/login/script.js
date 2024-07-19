(function(){
    $("#login-submit")
        .on("click", function(){
            let email = $("#login-input").val();
            if((/^\S+[\.\S+]*@\S+[\.\S+]+$/).test(email)) {
                window.Login(email, email.split("@")[0])
                    .then((userCredential) => {
                        console.log(userCredential);
                        // Signed in
                        var user = userCredential.user;
                        // ...
                        window.Notify("success", "OK");
                        window.HideOverlay();
                    })
                    .catch((error) => {
                        window.Notify("error", error.code);
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
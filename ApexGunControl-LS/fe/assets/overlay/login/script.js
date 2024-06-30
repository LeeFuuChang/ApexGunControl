$("#login-submit").on("click", function(){
    let email = $("#login-input").val();
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
});
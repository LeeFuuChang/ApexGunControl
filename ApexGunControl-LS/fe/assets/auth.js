window.auth = function() {
    if(typeof window.auth._i == "object") return window.auth._i;

    this.user = null;
    this.authorized = false;
    this.expireAt = null;

    this.authStateUpdate = () => {
        $.post("/app/auth-state")
            .done((expireAt)=>{
                if(this.authorized == !!expireAt) return;
                this.authorized = !!expireAt;
                this.expireAt = expireAt;
                this.authStateChanged();
            })
            .fail(()=>{
                if(!this.authorized) return;
                this.authorized = false;
                this.expireAt = null;
                this.authStateChanged();
            });
        this.authStateUpdateTimeout = setTimeout(this.authStateUpdate, 1000);
    };
    this.authStateUpdateTimeout = setTimeout(this.authStateUpdate, 1000);

    this.authStateChanged = () => {
        $("#side-login-button").css("display", !this.user?"flex":"none");
        $("#side-logout-button").css("display", this.user?"flex":"none");
        if(!this.authorized) window.LoadPage("dashboard");
        if(!this.user) window.LoadOverlay("login");
        if(this.user && this.authorized) window.RefreshPage();
    };

    this.post = (endpoint, data) => {
        return $.post(endpoint, data)
                    .done((response)=>{
                        if(response["username"] && response["password"]) {
                            this.user = response;
                            window.Notify("success", "OK");
                        }
                        else {
                            this.user = null;
                            window.Notify("error", "");
                        }
                    })
                    .fail((response)=>{
                        window.Notify("error", response.statusText);
                    })
                    .always(this.authStateChanged);
    };

    this.login = (username, password) => {
        return this.post("/app/login", {"username": username, "password": password});
    };

    this.activate = (pin) => {
        return this.post("/app/activate", {"pin": pin});
    };

    this.logout = () => {
        return this.post("/app/logout", {});
    };

    window.auth._i = this;

    return window.auth._i;
};

$(document).ready(function(){
    window.auth();
    $("#side-login-button").on("click", ()=>{
        window.LoadOverlay("login");
    });
    $("#side-logout-button").on("click", ()=>{
        window.auth().logout();
    });
});
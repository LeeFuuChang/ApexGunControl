window.auth = function() {
    if(typeof window.auth._i == "object") return window.auth._i;

    this.user = null;
    this.authorized = false;
    this.expireAt = null;

    this.authStateUpdate = () => {
        $.post("/auth/expiration")
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

    this.post = (endpoint, data, success) => {
        return $.post(endpoint, data)
                    .done((response)=>{
                        if(response["username"] && response["password"]) {
                            success(response)
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
        return this.post("/auth/login", {"username": username, "password": password}, (r)=>{this.user=r});
    };

    this.activate = (pin) => {
        return this.post("/auth/activate", {"pin": pin}, (r)=>{this.user=r});
    };

    this.logout = () => {
        return this.post("/auth/logout", {}, (r)=>{this.user=null});
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
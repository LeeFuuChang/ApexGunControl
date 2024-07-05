(function(){
    /*
    Event Binding Beg
    */
    function CheckPath(path) {
        let valid = path.toLowerCase().includes("apex") && path.endsWith("cfg");
        if(!valid) window.Notify("error", window.GetLangText("page-config-wrong-path"))
        return valid;
    };
    $(".directory input")
        .on("focusout", function(){
            let path = $(this).val();
            if(!CheckPath(path)) {
                $(this).val(null);
            }
        });
    $(".install-button")
        .on("click", function(){
            let path = $(".directory input").val();
            if(!CheckPath(path)) return;
            return new Promise((resolve, reject)=>{
                let data = { "path": path };
                for(let inp of $("input[path='cfg']")) {
                    data[$(inp).attr("name")] = $(inp).prop("checked");
                }
                return resolve(data);
            }).then((data)=>{
                return $.post("/app/config/cfg.json", JSON.stringify(data));
            }).then(()=>{
                return window.Notify("success", window.GetLangText("page-config-save-success"));
            });
        });
    /*
    Event Binding End
    */


    /*
    Load Data Beg
    */
    $.get("/app/config/cfg.json", {})
        .then((data)=>{
            $(".directory input").val(data.path);
            for(let inp of $("input[path='cfg']")) {
                $(inp).prop("checked", data[$(inp).attr("name")]);
            }
        });
    /*
    Load Data End
    */
})();


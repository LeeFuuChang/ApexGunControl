(function(){
    /*
    Event Binding Beg
    */
    $(".directory .directory-button")
        .on("click", function(){
            $(this).siblings("input[type='file']").click();
        });
    $(".directory input[type='file']")
        .on("change", function(){
            let path = $(this).val();
            let input = $(this).siblings("input[type='text']").val(path);
            let valid = path.toLowerCase().includes("apex") && path.endsWith("cfg");
            if(!valid) {
                window.Notify("error", window.GetLangText("page-config-wrong-path"))
                $(this).val(null);
                input.val(null);
            }
        });
    $(".directory input[type='text']")
        .on("focusout", function(){
            let path = $(this).val();
            let valid = path.toLowerCase().includes("apex") && path.endsWith("cfg");
            if(!valid) {
                $(this).val(null);
                window.Notify("error", window.GetLangText("page-config-wrong-path"))
            }
        })
})();


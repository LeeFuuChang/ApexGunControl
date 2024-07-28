(function(){
    function SaveAppConfig(){
        return $.post("/app/config/app.json", {
            "crash-report": $("input[name='crash-report']").is(":checked"),
            "language": $("input[type='radio'][name='language']:checked").attr("lang"),
            "window-scale": parseFloat($(":root").css("--scale"))
        });
    }


    /*
    Crash report
    */
    $("input[name='crash-report']").on("change", SaveAppConfig);


    /*
    Language
    */
    $(".checkbox[name='language']").on("change", function(){
        if($(this).is(":checked")) {
            window.SetLanguage($(this).attr("lang"));
            SaveAppConfig();
        }
    });


    /*
    Window Scaling
    */
    let scales = [
        0.75,
        0.80,
        0.90,
        1.00,
        1.10,
        1.25,
        1.50,
    ];

    function changeScaling(deltaIndex) {
        let idx = scales.indexOf(parseFloat($(":root").css("--scale")));
        idx = Math.max(0, Math.min(idx+deltaIndex, scales.length-1));
        $(".scale-text").text(`${(scales[idx]*100).toFixed(0)}%`);
        window.Resize(scales[idx]);
        SaveAppConfig();
    }

    $("#overlay-container .scale-button")
        .on("click", function(){
            switch($(this).data("symbol")) {
                case '-':
                    changeScaling(-1);
                    break;
                case '+':
                    changeScaling(+1);
                    break;
                default:
                    let idx = scales.indexOf(parseFloat($(":root").css("--scale")));
                    changeScaling(scales.indexOf(1.0) - idx);
                    break;
            }
        });


    /*
    Load Config
    */
    $.get("/app/config/app.json", {})
        .then((config)=>{
            $("span[name='current-version']").text(config["current-version"]);
            $("span[name='latest-version']").text(config["latest-version"]);
            $("span[name='release-date']").text(config["release-date"]);
            $("input[name='crash-report']").prop("checked", config["crash-report"]);
            $(`input[type='radio'][name='language'][lang='${config["language"]}']`).prop("checked", true);
            changeScaling(scales.indexOf(parseFloat(config["window-scale"])) - scales.indexOf(parseFloat($(":root").css("--scale"))));
        });
})();
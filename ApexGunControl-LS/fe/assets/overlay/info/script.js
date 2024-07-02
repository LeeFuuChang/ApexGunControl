(function(){
    /*
    Language
    */
    $(".checkbox[name='language']").on("change", function(){
        if($(this).is(":checked")) {
            $("#app").attr("lang", $(this).attr("lang"));
            window.ReloadPage();
        }
    });


    /*
    Window Scaling
    */
    let scales = [
        0.50,
        0.67,
        0.75,
        0.80,
        0.90,
        1.00,
        1.10,
        1.25,
        1.50,
    ];
    let changeScaling = function(deltaIndex) {
        let span = $("#overlay-container .block[name='window-scale'] span");
        let idx = parseInt(span.data("index"));
        idx = Math.max(0, Math.min(idx+deltaIndex, scales.length-1));
        span.data("index", idx).text(`${(scales[idx]*100).toFixed(0)}%`);
        window.Resize(scales[idx]);
    };
    $("#overlay-container .block[name='window-scale'] button[data-symbol='-']")
        .on("click", ()=>changeScaling(-1));
    $("#overlay-container .block[name='window-scale'] button[data-symbol='+']")
        .on("click", ()=>changeScaling(+1));
    $("#overlay-container .block[name='window-scale'] .reset-button")
        .on("click", ()=>{
            let span = $("#overlay-container .block[name='window-scale'] span");
            let idx = parseInt(span.data("index"));
            let tar = scales.indexOf(idx);
            changeScaling((tar<0?5:tar) - idx);
        });
})();
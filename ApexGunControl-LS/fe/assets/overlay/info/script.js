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
    let idx = scales.indexOf(parseFloat($(":root").css("--scale")));
    $(".scale-text").text(`${(scales[idx]*100).toFixed(0)}%`);
    let changeScaling = function(deltaIndex) {
        let idx = scales.indexOf(parseFloat($(":root").css("--scale")));
        idx = Math.max(0, Math.min(idx+deltaIndex, scales.length-1));
        $(".scale-text").text(`${(scales[idx]*100).toFixed(0)}%`);
        window.Resize(scales[idx]);
    };
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
})();
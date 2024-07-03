(function(){
    let slides = [
        "assets/media/installation/Step1.png",
        "assets/media/installation/Step2.png",
        "assets/media/installation/Step3.png",
        "assets/media/installation/Step4.png",
        "assets/media/installation/Step5.png",
        "assets/media/installation/Step6.png",
    ];
    $("#page[name='guide'] .image").css("--slide-index", 0);
    for(let path of slides) {
        $("#page[name='guide'] .image").append(`<img src="${path}" alt="">`);
        $("#page[name='guide'] nav ul").append("<li></li>");
    }
    $("#page[name='guide'] nav ul li").on("click", function(){
        $("#page[name='guide'] .image").css("--slide-index", $(this).index());
        $(this).addClass("active").siblings().removeClass("active");
    });
    $("#page[name='guide'] nav button").on("click", function(){
        let currentIndex = parseInt($("#page[name='guide'] .image").css("--slide-index"));
        let nextIndex = Math.max(1, Math.min(currentIndex+$(this).index(), $(".image img").length)) - 1;
        $("#page[name='guide'] .image").css("--slide-index", nextIndex);
        $("#page[name='guide'] nav ul li").removeClass("active").eq(nextIndex).addClass("active");
    });
})();
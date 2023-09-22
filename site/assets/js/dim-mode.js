const dim_buttons = document.querySelectorAll("#dim-button");
const body = document.querySelector("body");

const element_change_img = [
    [document.querySelector("#about-content-bubble-icon"), "assets/img/about/mockup.png", "assets/img/about/mockup-dim.png"],
    [document.querySelector("#header-logo-img"), "assets/img/header/logo.png", "assets/img/header/logo-dim.png"]
]

dim_buttons.forEach(dim_button => {
    dim_button.addEventListener("click", function(){
        console.log("ok");
        if(body.classList.contains("dim-mode")){
            body.classList.remove("dim-mode");
            element_change_img.forEach(element=>{
                element[0].src = element[1];
            })
        }else{
            body.classList.add("dim-mode");
            element_change_img.forEach(element=>{
                element[0].src = element[2];
            })
        }
    })
})



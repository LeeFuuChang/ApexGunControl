const hamburger_menu_button = document.querySelector("#hamburger-menu-button");
const hamburger_menu_link = document.querySelectorAll(".hamburger-menu-link");
const header = document.querySelector("#header");

hamburger_menu_button.addEventListener("click", function(){
    if(header.classList.contains("header-open")){
        header.classList.remove("header-open");
    } else {
        header.classList.add("header-open");
    }
})

hamburger_menu_link.forEach(link => {
    link.addEventListener("click", function(){
        header.classList.remove("header-open");
    })
})

window.onscroll = function(){
    if(window.scrollY > 10){
        header.classList.add("header-transparent");
    }else{
        header.classList.remove("header-transparent");
    }
}
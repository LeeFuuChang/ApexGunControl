document.querySelectorAll('a[href^="#"]').forEach(element => {
    element.addEventListener('click', function (e) {
        e.preventDefault();

        document.querySelector(element.getAttribute('href')).scrollIntoView({
            behavior: "smooth"
        });
    });
});
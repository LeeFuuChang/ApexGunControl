const firebaseConfig = {
    apiKey: "AIzaSyAYiAuEDRQt-98os2e8Gmw5Qh07Ih1iIaE",
    authDomain: "apexguncontrol-daaee.firebaseapp.com",
    projectId: "apexguncontrol-daaee",
    storageBucket: "apexguncontrol-daaee.appspot.com",
    messagingSenderId: "970669571754",
    appId: "1:970669571754:web:478fc877cb6c922ed0dad3",
    measurementId: "G-ZJ6BL6J1JB"
};

const firebaseApp = firebase.initializeApp(firebaseConfig);

firebase.auth().onAuthStateChanged((user)=>{
    $("#side-login-button").css("display", !user?"flex":"none");
    $("#side-logout-button").css("display", user?"flex":"none");

    window.LoadPage($("#page").attr("name"));

    if(user) {
        // User is signed in, see docs for a list of available properties
        // https://firebase.google.com/docs/reference/js/v8/firebase.User
        var uid = user.uid;
        // ...
    } else {
        // User is signed out
        // ...
    }
});

window.Login = function(acc) {
    return firebase.auth().signInWithEmailAndPassword(acc, acc.split("@")[0]);
};

$(document).ready(function(){
    $("#side-login-button").on("click", ()=>{
        window.LoadOverlay("login");
    });
    $("#side-logout-button").on("click", ()=>{
        firebase.auth().signOut().then(() => {
            // Sign-out successful.
        }).catch((error) => {
            // An error happened.
        });
    });
});
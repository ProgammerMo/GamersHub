
const loader = document.querySelector("#loader");
const login = document.querySelector("#login");
const register = document.querySelector("#register");
const regbutton = document.querySelector("#regbutton");
const loginbutton = document.querySelector("#loginbutton");

document.addEventListener("DOMContentLoaded", () => {
    
    loader.style.display = "none";
    
    if (page == "login"){
        login.style.height = "100%";
        login.style.width = "100%";
        }
        else {
        register.style.height = "100%";
        register.style.width = "100%";
    }

    regbutton.onclick = () => {
        login.style.height = "0";
        login.style.width = "0";
        setTimeout(() =>{
            register.style.height = "100%";
            register.style.width = "100%";
        }, 500)
    }
    
    loginbutton.onclick = () => {
        register.style.height = "0";
        register.style.width = "0";
        setTimeout(() =>{
            login.style.height = "100%";
            login.style.width = "100%";
        }, 500)
    }
})
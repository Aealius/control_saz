// Скрипт для смены видимости поля с паролем и его иконки 

let passwordToggle = document.getElementById("passwordToggle");
let password = document.getElementById("password");

passwordToggle.addEventListener('click', (e) => {
    let type = password.getAttribute('type') === 'password' ? 'text' : 'password';
    password.setAttribute('type', type);

    e.target.classList.toggle('fa-eye');
    e.target.classList.toggle('fa-eye-slash');
});
    
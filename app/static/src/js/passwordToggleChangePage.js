// Скрипт для смены видимости поля с паролем и его иконки для страницы смены пароля

let passwordToggleOld = document.getElementById("passwordToggleOld");
let oldpPassword = document.getElementById("old_password");

let passwordToggleNew = document.getElementById("passwordToggleNew");
let newPassword = document.getElementById("new_password");

let passwordToggleConfirm = document.getElementById("passwordToggleConfirm");
let confirmPassword = document.getElementById("confirm_password");

passwordToggleOld.addEventListener('click', (e) => {
    let type = oldpPassword.getAttribute('type') === 'password' ? 'text' : 'password';
    oldpPassword.setAttribute('type', type);

    e.target.classList.toggle('fa-eye');
    e.target.classList.toggle('fa-eye-slash');
});

passwordToggleNew.addEventListener('click', (e) => {
    let type = newPassword.getAttribute('type') === 'password' ? 'text' : 'password';
    newPassword.setAttribute('type', type);

    e.target.classList.toggle('fa-eye');
    e.target.classList.toggle('fa-eye-slash');
});
passwordToggleConfirm.addEventListener('click', (e) => {
    let type = confirmPassword.getAttribute('type') === 'password' ? 'text' : 'password';
    confirmPassword.setAttribute('type', type);

    e.target.classList.toggle('fa-eye');
    e.target.classList.toggle('fa-eye-slash');
});
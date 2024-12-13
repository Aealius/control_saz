let createMemoForm = document.getElementById("createMemoForm");

createMemoForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const base_url_api = window.location.origin + '/api';
    formData = new FormData(event.target);

    fetch(base_url_api + '/users/current_user_with_head')
        .then(responseUser => responseUser.json())
        .then(user => {
            if(user.full_department){
                formData.append("from", user.full_department);
            }
            else{
                formData.append("from", user.department);
            }
            
            formData.append("signerName",  user.headName[0] + '.' + user.headPatronymic[0] + '.' + user.headSurname);
            formData.append("signerPosition", user.headPosition);
            formData.append("filePathForSave",user.savePath);
            formData.append("signaturePath",user.headSignaturePath);

            fetch('https://localhost:44365' + '/Report/createMemoReport', {
                method: 'POST',
                body: formData,
            }).then((response) =>{
                console.log(response)
            }); 

            currentUserLogin = user.login;
        })
        .catch(console.error);

    
         

    // let validationResultArray = [checkExecutorSelectValidity(createMemoForm, executorSelect), checkDescriptionValidity(descriptionInput)];

    // if (validate(validationResultArray, createMemoForm)) {

        
    // }    
});

let optionsButtons = document.querySelectorAll(".option-button");
// Для выделения кнопок
let spacingButtons = document.querySelectorAll(".spacing");
let formatButtons = document.querySelectorAll(".format");
let scriptButtons = document.querySelectorAll(".script");

// Инициализирует выделение кнопок
const initializer = () => {
    highlighter(spacingButtons, true);
    highlighter(formatButtons, false);
    highlighter(scriptButtons, true);
};

// Выделение кнопок
// needsRemoval = true - значит, что только одна кнопка из группы должна выделятся
// false - могут быть выделены сразу несколько кнопок из группы
const highlighter = (className, needsRemoval) => {
    className.forEach((button) => {
        button.addEventListener("click", () => {
            if(needsRemoval){
                let alreadyActive = false;
                
                if(button.classList.contains("active")){
                    alreadyActive = true;
                }

                highlighterRemover(className);
                if(!alreadyActive){
                    button.classList.add("active");
                }
            }
            else{
                button.classList.toggle("active");
            }
        });
    });
};


// Основные 2 функции для работы текст. редактора
// execCommand не рекомендуется использовать из-за устаревания
// + она ведет себя по разному в разных браузерах
// Но на данный момент достаточно гибкой и лучшей альтернативы не нашлось
const modifyText = (command, defaultUi, value) => {
    document.execCommand(command, defaultUi, value);
};

optionsButtons.forEach(button => {
    button.addEventListener("click", () => {
        modifyText(button.id, false, null);
    });
});
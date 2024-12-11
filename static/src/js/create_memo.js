let createMemoForm = document.getElementById("createMemoForm");

createMemoForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const base_url_api = window.location.origin + '/api';

    formData = new FormData(event.target);

    // Подтягивать путь к подписи и путь для сейва
    formData.append("signaturePath","C:\\Users\\asup-maxim\\Downloads\\11.jpg");
    formData.append("filePathForSave","D:\\MB\\1\\control_saz\\uploads\\Test\\1.pdf");

    fetch(base_url_api + '/users/current_user')
        .then(responseUser => responseUser.json())
        .then(user => {


            formData.append("from", user.department);
            formData.append("signerName", "Иванов И. И.");
            formData.append("signerPosition", "Начальник отдела ...");


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
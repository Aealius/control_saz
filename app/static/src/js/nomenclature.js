document.getElementById('nm-select') && document.getElementById('nm-select').addEventListener('change', (e) =>{
    changeValue(e.target.value);
});

function changeValue(el){
    let numberInput = document.getElementById('nm-number');
    if (el === "-1"){
        numberInput.disabled = true;
        numberInput.value = "";
    }
    else{
        numberInput.disabled = false;

        let nm_arr_str = localStorage.getItem('nm');
        let nm_arr = JSON.parse(nm_arr_str);
        let current_doc = nm_arr[el - 1];
    
        numberInput.value = current_doc.counter + 1;
    }
}
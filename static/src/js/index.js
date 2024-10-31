let senderSelect = document.getElementById("select-task-sender"); //дропдаун с выбором входящих/исходящих тасок
let urlParams  = new URLSearchParams(window.location.search);

document.addEventListener('DOMContentLoaded', () => { //задает значение дропдауна из значения, переданного в строке параметров
    
    let senderValue = urlParams.get('sn') ? urlParams.get('sn') : "in";

    document.getElementById("select-task-sender").querySelector("option[value='" + senderValue + "']").selected = true;
});


senderSelect.addEventListener('change', () => {
    let senderValue = senderSelect.value;

    window.location.href = buildQueryString(senderValue);
});


function buildQueryString(senderValue){ //построение строки параметров для последующей фильтрации по отправителю

    let newUrl =  new URL(window.location.origin + window.location.pathname);

    if (window.location.search !== ''){
        let urlParams = new URLSearchParams(window.location.search);
        let snParamValue = urlParams.get('sn');

        if(snParamValue == null){
            newUrl.searchParams.append('sn', senderValue);
            newUrl.searchParams.set('p', 1);
            //newUrl += window.location.search + `&sn=${senderValue}` + window.location.search.replace(`p=${pageParamValue}`, '&p=1');
        }
        else{
            newUrl.searchParams.set('sn', senderValue);
            newUrl.searchParams.set('p', 1);
        }
    }
    else{
        newUrl.searchParams.set('sn', senderValue);
        newUrl.searchParams.set('p', 1);
    }

    return newUrl;
}

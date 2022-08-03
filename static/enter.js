const input = document.getElementById('text');

function Alert(){
    alert(input.value);
}

input.addEventListener('keyup', (e) => {
    if (e.keyCode === 13) {
        Alert();
    }
}
);
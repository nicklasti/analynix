// Empty JS for your own code to be here

const input = document.getElementById('input');
    
input.addEventListener('keyup', (e) => {
        if (e.keyCode === 13) {
            e.preventDefault()
            console.log('submit')
        }
    }
);

registerForm.addEventListener('keyup', (e) => {
        if(e.keyCode === 13) {
            e.preventDefault();
            registerForm.submit();
        }
    }
);
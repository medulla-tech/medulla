document.addEventListener('DOMContentLoaded', function () {
    const radioAddDevice = document.getElementById('radio_enrol');
    const radioConfigure = document.getElementById('radio_configure');
    const formAddDevice = document.getElementById('form_enrol');
    const formConfigure = document.getElementById('form_configure');

    function toggleForms() {
        if (radioAddDevice.checked) {
            formAddDevice.style.display = 'block';
            formConfigure.style.display = 'none';
        } else if (radioConfigure.checked) {
            formAddDevice.style.display = 'none';
            formConfigure.style.display = 'block';
        }
    }

    radioAddDevice.addEventListener('change', toggleForms);
    radioConfigure.addEventListener('change', toggleForms);
    toggleForms();
});

document.addEventListener('DOMContentLoaded', function () {
    const radioEnrol = document.getElementById('radio_enrol');
    const radioConfigure = document.getElementById('radio_configure');
    const formEnrol = document.getElementById('form_enrol');
    const formConfigure = document.getElementById('form_configure');

    function toggleForms() {
        if (radioEnrol.checked) {
            formEnrol.style.display = 'block';
            formConfigure.style.display = 'none';
        } else if (radioConfigure.checked) {
            formEnrol.style.display = 'none';
            formConfigure.style.display = 'block';
        }
    }

    radioEnrol.addEventListener('change', toggleForms);
    radioConfigure.addEventListener('change', toggleForms);
    toggleForms();
});

// Mostrar/ocultar contraseña
document.addEventListener('DOMContentLoaded', function () {
    const tablas = document.querySelectorAll('table');

    if (tablas.length > 0) {
        tablas.forEach(function (tabla) {
            $(tabla).DataTable({
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json'
                },
                pageLength: 10,
                lengthChange: false,
                ordering: true,
                order: [],
                info: false,
                searching: true,
                pagingType: 'simple_numbers',
                responsive: true,
                dom: '<"top"f>rt<"bottom"p><"clear">'
            });
        });
    }

    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('passwordInput');
    const passwordIcon = document.getElementById('passwordIcon');

    if (togglePassword) {
        togglePassword.addEventListener('click', function () {
            const isVisible = passwordInput.type === 'text';
            passwordInput.type = isVisible ? 'password' : 'text';
            passwordIcon.classList.toggle('bi-eye');
            passwordIcon.classList.toggle('bi-eye-slash');
        });
    }

    // Activar tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle=\"tooltip\"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});


function capitalizarPalabras(input) {
    input.value = input.value
        .toLowerCase()
        .replace(/\b\w/g, letra => letra.toUpperCase());
}
document.addEventListener('DOMContentLoaded', function () {
    const selectArea = document.querySelector('select[name="area_id"]');
    if (selectArea) {
        $(selectArea).select2({
            theme: 'bootstrap-5',
            width: '100%',
            language: 'es',
            placeholder: 'Seleccione un área',
            dropdownParent: $('#modalUsuario'),
            allowClear: true
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.fila-usuario').forEach(row => {
        row.addEventListener('click', (e) => {
            // Evita si hace clic en un botón o formulario
            if (e.target.closest('button') || e.target.closest('form')) return;

            // Verifica si la fila está marcada como admin
            if (row.classList.contains('protegido')) {
                // Opcional: mostrar tooltip o alerta
                mostrarToast("Esta cuenta está protegida y no se puede editar.");
                return;
            }

            const id = row.getAttribute('data-id');
            editarUsuario(id);
        });
    });
});


function mostrarToast(mensaje) {
    const toastEl = document.getElementById('toastMensaje');
    const toastTexto = document.getElementById('toastTexto');
    toastTexto.innerText = mensaje;

    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}




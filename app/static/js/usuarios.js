document.addEventListener('DOMContentLoaded', function () {
    // Activar tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(el => new bootstrap.Tooltip(el));

    // Mostrar/Ocultar contraseña
    const togglePasswordUser = document.getElementById('togglePasswordUser');
    const passwordInputUser = document.getElementById('passwordInputUser');
    const passwordIconUser = document.getElementById('passwordIconUser');

    if (togglePasswordUser) {
        togglePasswordUser.addEventListener('click', () => {
            const isVisible = passwordInputUser.type === 'text';
            passwordInputUser.type = isVisible ? 'password' : 'text';
            passwordIconUser.classList.toggle('bi-eye');
            passwordIconUser.classList.toggle('bi-eye-slash');
        });
    }

    const toggleConfirm = document.getElementById('toggleConfirm');
    const confirmInput = document.getElementById('confirmInput');
    const confirmIcon = document.getElementById('confirmIcon');

    if (toggleConfirm) {
        toggleConfirm.addEventListener('click', () => {
            const isVisible = confirmInput.type === 'text';
            confirmInput.type = isVisible ? 'password' : 'text';
            confirmIcon.classList.toggle('bi-eye');
            confirmIcon.classList.toggle('bi-eye-slash');
        });
    }

    // Mostrar modal para registrar
    window.nuevoUsuario = function () {
        const form = document.getElementById('formUsuario');
        const modal = document.getElementById('modalUsuario');
        const passwordFields = modal.querySelectorAll('.campos-password');
        const modo = form.querySelector('#modoFormulario');

        form.reset();
        form.action = '/usuarios/registrar';
        document.getElementById('modalUsuarioLabel').innerText = 'Registrar Usuario';
        modo.value = 'crear';

        passwordFields.forEach(el => el.classList.remove('d-none'));
        bootstrap.Modal.getOrCreateInstance(modal).show();
    }

    // Mostrar modal para editar
    window.editarUsuario = function (id) {
        fetch(`/usuarios/editar/${id}`)
            .then(res => res.json())
            .then(data => {
                const form = document.getElementById('formUsuario');
                const modal = document.getElementById('modalUsuario');
                const passwordFields = modal.querySelectorAll('.campos-password');
                const modo = form.querySelector('#modoFormulario');

                form.action = `/usuarios/actualizar/${id}`;
                document.getElementById('modalUsuarioLabel').innerText = 'Editar Usuario';
                modo.value = 'editar';

                form.username.value = data.username;
                form.nombre_completo.value = data.nombre_completo;
                form.correo.value = data.correo;
                form.celular.value = data.celular;
                form.area_id.value = data.area_id;
                form.es_admin.checked = data.es_admin;
                form.password.value = '';
                form.confirm.value = '';

                passwordFields.forEach(el => el.classList.add('d-none'));

                bootstrap.Modal.getOrCreateInstance(modal).show();
            });
    }

    // Validar y enviar formulario
    const form = document.getElementById('formUsuario');
    const password = document.getElementById('passwordInputUser');
    const confirm = document.getElementById('confirmInput');
    const confirmFeedback = confirm.parentElement.nextElementSibling;
    const modo = document.getElementById('modoFormulario');

    form.addEventListener('submit', function (event) {
        console.log('== INICIO DEL SUBMIT ==');
        event.preventDefault();

        const modo = document.getElementById('modoFormulario');
        const password = document.getElementById('passwordInputUser');
        const confirm = document.getElementById('confirmInput');
        const confirmFeedback = confirm.parentElement.nextElementSibling;

        const esEdicion = modo.value === 'editar';
        let valido = true;

        console.log('Submit interceptado. Acción:', form.action);
        console.log('Modo:', modo.value);

        confirm.classList.remove('is-invalid');
        confirm.setCustomValidity('');
        confirmFeedback.style.display = 'none';

        if (esEdicion) {
            password.removeAttribute('required');
            confirm.removeAttribute('required');
        }

        if (!esEdicion && password.value !== confirm.value) {
            confirm.classList.add('is-invalid');
            confirm.setCustomValidity('Las contraseñas no coinciden.');
            confirmFeedback.style.display = 'block';
            valido = false;
        }

        if (!form.checkValidity() || !valido) {
            form.classList.add('was-validated');
            return;
        }

        const formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        icon: 'success',
                        title: modo.value === 'editar' ? 'Usuario actualizado' : 'Usuario registrado',
                        timer: 2000,
                        showConfirmButton: false
                    });
                    recargarUsuarios();
                    bootstrap.Modal.getInstance(document.getElementById('modalUsuario')).hide();
                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: data.errors.join('\n'),
                        confirmButtonText: 'Entendido'
                    });
                }
            });
    });

});
function confirmarEliminacion(id) {
    Swal.fire({
        title: '¿Eliminar usuario?',
        text: 'Esta acción no se puede deshacer.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    }).then(result => {
        if (result.isConfirmed) {
            fetch(`/usuarios/eliminar/${id}`, {
                method: 'POST'
            }).then(() => {
                Swal.fire({
                    icon: 'success',
                    title: 'Usuario eliminado',
                    showConfirmButton: false,
                    timer: 1800
                });
                recargarUsuarios();
            });
        }
    });
}


function confirmarToggleEstado(id, activo) {
    // Convertimos string 'True'/'False' a booleano real
    const isActive = (activo === 'True');  
    const accion = isActive ? 'desactivar' : 'activar';
    Swal.fire({
        title: `¿Deseas ${accion} este usuario?`,
        text: `El usuario será marcado como ${isActive ? 'inactivo' : 'activo'}.`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: `Sí, ${accion}`,
        cancelButtonText: 'Cancelar'
    }).then(result => {
        if (result.isConfirmed) {
            fetch(`/usuarios/toggle_estado/${id}`, {
                method: 'POST'
            })
                .then(() => {
                    Swal.fire({
                        icon: 'success',
                        title: `Usuario ${isActive ? 'desactivado' : 'activado'}`,
                        showConfirmButton: false,
                        timer: 1800
                    });
                    recargarUsuarios(); // función que recarga la tabla
                });
        }
    });
}


function recargarUsuarios() {
    fetch('/usuarios/lista')
        .then(res => res.text())
        .then(html => {
            document.getElementById('tablaUsuarios').innerHTML = html;
            inicializarTodasLasTablas();
        });
       
}
function inicializarTodasLasTablas() {
    const tablas = document.querySelectorAll('table.data-table'); // Solo las que tengan clase .data-table
    tablas.forEach(tabla => {
        if (!$.fn.DataTable.isDataTable(tabla)) { // Evitar inicializar dos veces
            $(tabla).DataTable({
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.13.4/i18n/es-ES.json'
                },
                pagingType: 'simple',
                pageLength: 8,
                lengthChange: false,
                searching: true,
                ordering: false,
                info: false,
                autoWidth: false,
                responsive: true
            });
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    // Mostrar modal para nueva área
    window.nuevaArea = function () {
        const form = document.getElementById('formArea');
        form.reset();
        form.action = '/areas/registrar';
        document.getElementById('modalAreaLabel').innerText = 'Registrar Área';
        document.getElementById('modoFormulario').value = 'crear';
        bootstrap.Modal.getOrCreateInstance(document.getElementById('modalArea')).show();
    };


    
    // Mostrar modal para editar área
    window.editarArea = function (id) {
        fetch(`/areas/editar/${id}`)
            .then(res => res.json())
            .then(data => {
                const form = document.getElementById('formArea');
                form.action = `/areas/actualizar/${id}`;
                document.getElementById('modalAreaLabel').innerText = 'Editar Área';
                document.getElementById('modoFormulario').value = 'editar';
                form.nombre.value = data.nombre;
         
                bootstrap.Modal.getOrCreateInstance(document.getElementById('modalArea')).show();
            });
    };

    // Validar y enviar formulario
    const form = document.getElementById('formArea');
    form.addEventListener('submit', function (event) {
        event.preventDefault();

        if (!form.checkValidity()) {
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
                        title: form.querySelector('#modoFormulario').value === 'editar' ? 'Área actualizada' : 'Área registrada',
                        showConfirmButton: false,
                        timer: 1800
                    });
                    recargarAreas();
                    bootstrap.Modal.getInstance(document.getElementById('modalArea')).hide();
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

    // Eliminar área con confirmación
    window.confirmarEliminacionArea = function (id) {
        Swal.fire({
            title: '¿Eliminar esta área?',
            text: 'Esta acción no se puede deshacer.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar'
        }).then(result => {
            if (result.isConfirmed) {
                fetch(`/areas/eliminar/${id}`, {
                    method: 'POST'
                }).then(() => {
                    Swal.fire({
                        icon: 'success',
                        title: 'Área eliminada',
                        showConfirmButton: false,
                        timer: 1800
                    });
                    recargarAreas();
                });
            }
        });
    };

 

   
});
function confirmarToggleEstadoArea(id, activo) {
    // Convertimos string 'True'/'False' a booleano real
    const isActive = (activo === 'True');
    const accion = isActive ? 'desactivar' : 'activar';
    Swal.fire({
        title: `¿Deseas ${accion} esta area?`,
        text: `El area será marcada como ${isActive ? 'inactiva' : 'activa'}.`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: `Sí, ${accion}`,
        cancelButtonText: 'Cancelar'
    }).then(result => {
        if (result.isConfirmed) {
            fetch(`/areas/toggle_estado/${id}`, {
                method: 'POST'
            })
                .then(() => {
                    Swal.fire({
                        icon: 'success',
                        title: `Area ${isActive ? 'desactivada' : 'activada'}`,
                        showConfirmButton: false,
                        timer: 1800
                    });
                    recargarAreas(); 
                });
        }
    });
}
// Recargar la lista de áreas
function recargarAreas() {
    fetch('/areas/lista')
        .then(res => res.text())
        .then(html => {
            document.getElementById('tablaAreas').innerHTML = html;
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

// static/js/documentos.js

let rutaCarpetas = []; // Mantener ruta actual


// Iniciar al cargar la página
document.addEventListener('DOMContentLoaded', function () {
    cargarCarpetaContenido(null); // Mostrar raíz

    // Evento para crear carpeta
    const formNuevaCarpeta = document.getElementById('formNuevaCarpeta');
    formNuevaCarpeta.addEventListener('submit', function (e) {
        e.preventDefault();
        crearCarpeta();
    });
    document.getElementById('formEditarDocumento').addEventListener('submit', function (e) {
        e.preventDefault();
        editarDocumento();
    });
    document.getElementById('formSubirDocumento').addEventListener('submit', function (e) {
        e.preventDefault();
        subirDocumento();
    });

});

function cargarCarpetaContenido(parentId) {
    const contenedor = document.getElementById('contenedorDocumentos');
    contenedor.innerHTML = '';

    fetch(`/carpetas/contenido/${parentId || ''}`)
        .then(res => res.json())
        .then(data => {
            actualizarBreadcrumb();

            if (data.carpetas.length === 0 && data.documentos.length === 0) {
                contenedor.innerHTML = '<p class="text-muted">Esta carpeta está vacía.</p>';
                return;
            }

            // Mostrar carpetas
            data.carpetas.forEach(carpeta => {
                const col = document.createElement('div');
                col.className = 'col-6 col-md-3 col-lg-2';

                const div = document.createElement('div');
                div.className = 'carpeta-card text-center';
                div.onclick = () => abrirSubcarpeta(carpeta.id, carpeta.nombre);

                div.innerHTML = `
                    <i class="bi bi-folder-fill carpeta-icono"></i>
                    <div class="small fw-semibold">${carpeta.nombre}</div>
                `;

                if (esAdmin === "true") {
                    const acciones = document.createElement('div');
                    acciones.className = 'mt-2 d-flex justify-content-center gap-2';

                    acciones.innerHTML = `
                        <button class="btn btn-sm btn-outline-primary" onclick="event.stopPropagation(); mostrarModalEditarCarpeta(${carpeta.id}, '${carpeta.nombre}')">
                            <i class="bi bi-pencil-square"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="event.stopPropagation(); confirmarEliminarCarpeta(${carpeta.id}, '${carpeta.nombre}')">
                            <i class="bi bi-trash"></i>
                        </button>
                    `;
                    div.appendChild(acciones);
                }

                col.appendChild(div);
                contenedor.appendChild(col);
            });

            // Mostrar documentos
            data.documentos.forEach(doc => {
                const col = document.createElement('div');
                col.className = 'col-6 col-md-3 col-lg-2';

                const div = document.createElement('div');
                div.className = 'documento-card text-center';

                div.onclick = () => {
                    if (doc.tipo === 'excel') {
                        div.onclick = () => abrirDocumento(doc.ruta_archivo, doc.id);
                    } else {
                        window.open('/' + doc.ruta_archivo, 'popupPDF', 'width=1000,height=700,scrollbars=yes,resizable=yes');
                        // Abre PDF
                    }
                };

                let icono = doc.tipo === 'excel' ? 'bi-file-earmark-excel' : 'bi-file-earmark-pdf';

                div.innerHTML = `
                    <i class="bi ${icono} documento-icono"></i>
                    <div class="small fw-semibold">${doc.nombre}</div>
                `;

                if (esAdmin === "true") {
                    const acciones = document.createElement('div');
                    acciones.className = 'mt-2 d-flex justify-content-center gap-2';

                    acciones.innerHTML = `
                        <button class="btn btn-sm btn-outline-primary" onclick="event.stopPropagation(); mostrarModalEditarDocumento(${doc.id}, '${doc.nombre}')">
                            <i class="bi bi-pencil-square"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="event.stopPropagation(); confirmarEliminarDocumento(${doc.id}, '${doc.nombre}')">
                            <i class="bi bi-trash"></i>
                        </button>
                    `;
                    div.appendChild(acciones);
                }

                col.appendChild(div);
                contenedor.appendChild(col);
            });

        });
}



function abrirSubcarpeta(id, nombre) {
    rutaCarpetas.push({ id, nombre });
    cargarCarpetaContenido(id);
}

function actualizarBreadcrumb() {
    const breadcrumb = document.getElementById('breadcrumb');
    breadcrumb.innerHTML = '';

    const home = document.createElement('span');
    home.innerHTML = `<i class="bi bi-house-door"></i> Inicio`;
    home.classList.add('breadcrumb-link');
    home.style.cursor = 'pointer';
    home.onclick = () => {
        rutaCarpetas = [];
        cargarCarpetaContenido(null);
    };
    breadcrumb.appendChild(home);

    rutaCarpetas.forEach((carpeta, index) => {
        const separator = document.createElement('span');
        separator.textContent = ' / ';
        breadcrumb.appendChild(separator);

        const link = document.createElement('span');
        link.innerHTML = `📂 ${carpeta.nombre}`;
        link.classList.add('breadcrumb-link');
        link.style.cursor = 'pointer';
        link.onclick = () => {
            rutaCarpetas = rutaCarpetas.slice(0, index + 1);
            cargarCarpetaContenido(carpeta.id);
        };
        breadcrumb.appendChild(link);
    });
}



function mostrarModalNuevaCarpeta() {
    bootstrap.Modal.getOrCreateInstance(document.getElementById('modalNuevaCarpeta')).show();
}

function mostrarToast(mensaje) {
    Swal.fire({
        icon: 'warning',
        title: mensaje,
        toast: true,
        position: 'top-end',
        timer: 2500,
        showConfirmButton: false
    });
}

function crearCarpeta() {
    const nombre = document.getElementById('nombreCarpeta').value.trim();
    const parentId = rutaCarpetas.length > 0 ? rutaCarpetas[rutaCarpetas.length - 1].id : null;

    if (!nombre) {
        mostrarToast('El nombre de la carpeta no puede estar vacío.');
        return;
    }

    fetch('/carpetas/crear', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre: nombre, parent_id: parentId })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Carpeta creada',
                    timer: 1800,
                    showConfirmButton: false
                });
                bootstrap.Modal.getInstance(document.getElementById('modalNuevaCarpeta')).hide();
                cargarCarpetaContenido(parentId);
                document.getElementById('formNuevaCarpeta').reset();
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.error || 'No se pudo crear la carpeta.'
                });
            }
        });
}


// Mostrar el modal de editar
function mostrarModalEditarCarpeta(id, nombreActual) {
    document.getElementById('editarCarpetaId').value = id;
    document.getElementById('editarNombreCarpeta').value = nombreActual;
    bootstrap.Modal.getOrCreateInstance(document.getElementById('modalEditarCarpeta')).show();
}

// Enviar edición al servidor
document.getElementById('formEditarCarpeta').addEventListener('submit', function (e) {
    e.preventDefault();
    editarCarpeta();
});

function editarCarpeta() {
    const id = document.getElementById('editarCarpetaId').value;
    const nuevoNombre = document.getElementById('editarNombreCarpeta').value.trim();

    if (!nuevoNombre) {
        mostrarToast('El nombre no puede estar vacío.');
        return;
    }

    const formData = new FormData();
    formData.append('nombre', nuevoNombre);

    fetch(`/carpetas/actualizar/${id}`, {
        method: 'POST',
        body: formData
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Nombre actualizado',
                    timer: 1500,
                    showConfirmButton: false
                });
                bootstrap.Modal.getInstance(document.getElementById('modalEditarCarpeta')).hide();
                const parentId = rutaCarpetas.length > 0 ? rutaCarpetas[rutaCarpetas.length - 1].id : null;
                cargarCarpetaContenido(parentId);
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.error || 'No se pudo actualizar la carpeta.'
                });
            }
        });
}


function confirmarEliminarCarpeta(id, nombre) {
    Swal.fire({
        title: '¿Eliminar carpeta?',
        text: `¿Deseas eliminar la carpeta "${nombre}"?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#d33'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/carpetas/eliminar/${id}`, {
                method: 'POST'
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Carpeta eliminada',
                            timer: 1500,
                            showConfirmButton: false
                        });
                        const parentId = rutaCarpetas.length > 0 ? rutaCarpetas[rutaCarpetas.length - 1].id : null;
                        cargarCarpetaContenido(parentId);
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: data.error || 'No se pudo eliminar la carpeta.'
                        });
                    }
                });
        }
    });
}


function mostrarModalEditarDocumento(id, nombreActual) {
    document.getElementById('editarDocumentoId').value = id;
    document.getElementById('editarNombreDocumento').value = nombreActual;
    document.getElementById('editarArchivoDocumento').value = ''; // Limpiar archivo anterior
    bootstrap.Modal.getOrCreateInstance(document.getElementById('modalEditarDocumento')).show();
}


function confirmarEliminarDocumento(id, nombre) {
    Swal.fire({
        title: '¿Eliminar documento?',
        text: `¿Deseas eliminar el documento "${nombre}"?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#d33'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/documentos/eliminar/${id}`, {
                method: 'POST'
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Documento eliminado',
                            timer: 1500,
                            showConfirmButton: false
                        });
                        const parentId = rutaCarpetas.length > 0 ? rutaCarpetas[rutaCarpetas.length - 1].id : null;
                        cargarCarpetaContenido(parentId);
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: data.error || 'No se pudo eliminar el documento.'
                        });
                    }
                });
        }
    });
}


function editarDocumento() {
    const id = document.getElementById('editarDocumentoId').value;
    const nombre = document.getElementById('editarNombreDocumento').value.trim();
    const archivo = document.getElementById('editarArchivoDocumento').files[0];

    if (!nombre) {
        mostrarToast('El nombre no puede estar vacío.');
        return;
    }

    const formData = new FormData();
    formData.append('nombre', nombre);
    if (archivo) {
        formData.append('archivo', archivo);
    }
    if (archivo) {
        const extPermitidas = ['pdf', 'xls', 'xlsx'];
        const ext = archivo.name.split('.').pop().toLowerCase();
        if (!extPermitidas.includes(ext)) {
            mostrarToast('Archivo no permitido. Solo PDF o Excel.');
            return;
        }
    }

    fetch(`/documentos/actualizar/${id}`, {
        method: 'POST',
        body: formData
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Documento actualizado',
                    timer: 1500,
                    showConfirmButton: false
                });
                bootstrap.Modal.getInstance(document.getElementById('modalEditarDocumento')).hide();
                const parentId = rutaCarpetas.length > 0 ? rutaCarpetas[rutaCarpetas.length - 1].id : null;
                cargarCarpetaContenido(parentId);
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.error || 'No se pudo actualizar el documento.'
                });
            }
        });
}

function mostrarModalSubirDocumento() {
    bootstrap.Modal.getOrCreateInstance(document.getElementById('modalSubirDocumento')).show();
}


function subirDocumento() {
    const nombre = document.getElementById('nombreDocumento').value.trim();
    const correo = document.getElementById('correoDocumento').value.trim();
    const archivo = document.getElementById('archivoDocumento').files[0];
    const carpetaId = rutaCarpetas.length > 0 ? rutaCarpetas[rutaCarpetas.length - 1].id : null;

    if (!nombre || !archivo || !correo){
        mostrarToast('Todos los campos son obligatorios.');
        return;
    }

    const extPermitidas = ['pdf', 'xls', 'xlsx'];
    const ext = archivo.name.split('.').pop().toLowerCase();

    if (!extPermitidas.includes(ext)) {
        mostrarToast('Archivo no permitido. Solo PDF o Excel.');
        return;
    }

    const tipo = ext === 'pdf' ? 'pdf' : 'excel';

    const formData = new FormData();
    formData.append('nombre', nombre);
    formData.append('correo', correo);
    formData.append('archivo', archivo);
    formData.append('carpeta_id', carpetaId);
    formData.append('tipo', tipo);

    fetch('/documentos/subir', {
        method: 'POST',
        body: formData
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Documento subido',
                    timer: 1500,
                    showConfirmButton: false
                });
                bootstrap.Modal.getInstance(document.getElementById('modalSubirDocumento')).hide();
                document.getElementById('formSubirDocumento').reset();
                cargarCarpetaContenido(carpetaId);
            } else if (data.existe) {
                Swal.fire({
                    title: 'Documento existente',
                    text: data.mensaje,
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'Sí, reemplazar',
                    cancelButtonText: 'Cancelar',
                    confirmButtonColor: '#d33'
                }).then((result) => {
                    if (result.isConfirmed) {
                        fetch('/documentos/subir?reemplazar=1', {
                            method: 'POST',
                            body: formData
                        })
                            .then(res => res.json())
                            .then(data => {
                                if (data.success) {
                                    Swal.fire({
                                        icon: 'success',
                                        title: 'Documento reemplazado',
                                        timer: 1500,
                                        showConfirmButton: false
                                    });
                                    bootstrap.Modal.getInstance(document.getElementById('modalSubirDocumento')).hide();
                                    document.getElementById('formSubirDocumento').reset();
                                    cargarCarpetaContenido(carpetaId);
                                } else {
                                    Swal.fire({
                                        icon: 'error',
                                        title: 'Error',
                                        text: data.error || 'No se pudo reemplazar el documento.'
                                    });
                                }
                            });
                    }
                });
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.error || 'No se pudo subir el documento.'
                });
            }
        });
}


function restaurarDocumento(id) {
    const boton = document.getElementById('btn-restaurar-' + id);
    if (!boton) return;

    boton.disabled = true;
    boton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Restaurando...';

    fetch(`/documentos/recuperar/${id}`, {
        method: 'POST'
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Documento restaurado',
                    timer: 1500,
                    showConfirmButton: false
                }).then(() => location.reload());
            } else {
                throw new Error("Error en respuesta");
            }
        })
        .catch(() => {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'No se pudo restaurar el documento.'
            });
            boton.disabled = false;
            boton.innerHTML = '<i class="bi bi-arrow-counterclockwise"></i> Restaurar';
        });
}


function volverACarpetas() {
    Swal.fire({
        title: 'Redirigiendo...',
        text: 'Volviendo a la vista de carpetas',
        icon: 'info',
        showConfirmButton: false,
        allowOutsideClick: false,
        timer: 1500,
        didOpen: () => {
            Swal.showLoading();
        }
    });

    setTimeout(() => {
        window.location.href = '/carpetas';
    }, 1000); // da tiempo al usuario de ver el SweetAlert
}


// Descargar una copia editable
function descargarCopiaExcel() {
    const urlCopia = `/documentos/descargar_copia?archivo=${encodeURIComponent(rutaDocumentoActual)}`;
    window.location.href = urlCopia;
}

// Toma la tabla HTML y la convierte a Excel
function guardarCopiaExcel() {
    const tabla = document.getElementById('excelPreviewTable');
    const datos = [];
    for (const fila of tabla.rows) {
        const filaDatos = [];
        for (const celda of fila.cells) {
            filaDatos.push(celda.textContent);
        }
        datos.push(filaDatos);
    }

    const hoja = XLSX.utils.aoa_to_sheet(datos);
    const libro = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(libro, hoja, "Hoja1");

    const wbout = XLSX.write(libro, { bookType: 'xlsx', type: 'array' });
    const blob = new Blob([wbout], { type: 'application/octet-stream' });

    const formData = new FormData();
    formData.append('archivo', blob, excelFilename);

    fetch('/documentos/guardar_copia_excel', {
        method: 'POST',
        body: formData
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Copia guardada',
                    text: 'La copia del Excel fue guardada exitosamente',
                    timer: 2000,
                    showConfirmButton: false
                });
                bootstrap.Modal.getInstance(document.getElementById('modalEditarExcel')).hide();
            } else {
                Swal.fire('Error', data.error || 'No se pudo guardar la copia.', 'error');
            }
        });
}

let rutaDocumentoActual = '';
let nombreDocumentoActual = '';

let documentoIdActual = null;
let documentoIdSeleccionado = null;  // Este se establecerá cuando se abra el modal
function abrirDocumento(ruta, idDocumento = null) {
    if (!ruta.endsWith('.xlsx') && !ruta.endsWith('.xls')) {
        window.open('/' + ruta, '_blank');
        return;
    }

    documentoIdSeleccionado = idDocumento;

    const nombre = ruta.split('/').pop();
    document.getElementById('nombreArchivoExcel').textContent = nombre;
    document.getElementById('btnDescargarCopia').href = '/' + ruta;

    bootstrap.Modal.getOrCreateInstance(document.getElementById('modalOpcionesExcel')).show();
}





function enviarCopiaRevision() {
    const input = document.getElementById('archivoEditadoInput');
    
    input.onchange = () => {
        const archivo = input.files[0];
        if (!archivo) return;

        const formData = new FormData();
        formData.append('archivo', archivo);

        Swal.fire({
            title: 'Enviando copia...',
            allowOutsideClick: false,
            didOpen: () => Swal.showLoading()
        });

        fetch(`/documentos/subir_copia_revision/${documentoIdSeleccionado}`, {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            Swal.close();

            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Copia enviada para revisión',
                    timer: 1800,
                    showConfirmButton: false
                });
                bootstrap.Modal.getInstance(document.getElementById('modalOpcionesExcel')).hide();
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.error || 'No se pudo enviar la copia.'
                });
            }
        });
    };

    // Disparar selección de archivo
    input.click();
}

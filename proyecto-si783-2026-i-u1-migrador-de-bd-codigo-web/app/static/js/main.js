const puertosDefault = {
    'MySQL': '3306',
    'PostgreSQL': '5432',
    'Oracle': '1521',
    'Microsoft SQL Server': '1433',
    'MongoDB': '27017',
    'Redis': '6379',
    'Elasticsearch': '9200',
    'Apache Cassandra': '9042'
};

function actualizarPuerto(tipo) {
    const motor = document.getElementById(tipo + '-motor').value;
    const puerto = puertosDefault[motor] || '';
    document.getElementById(tipo + '-puerto').value = puerto;
}

function obtenerDatosConexion(tipo) {
    return {
        tipo: tipo,
        motor: document.getElementById(tipo + '-motor').value,
        host: document.getElementById(tipo + '-host').value,
        puerto: document.getElementById(tipo + '-puerto').value,
        usuario: document.getElementById(tipo + '-usuario').value,
        contrasena: document.getElementById(tipo + '-contrasena').value,
        nombre_bd: document.getElementById(tipo + '-bd').value
    };
}

async function probarConexion(tipo) {
    const estado = document.getElementById(tipo + '-estado');
    estado.textContent = 'Probando...';
    estado.style.color = '#FFC107';
    
    try {
        const respuesta = await fetch('/api/probar-conexion', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(obtenerDatosConexion(tipo))
        });
        
        const datos = await respuesta.json();
        
        if (datos.estado === 'exito') {
            estado.textContent = 'Conectado';
            estado.style.color = '#4CAF50';
        } else {
            estado.textContent = 'Error: ' + datos.mensaje;
            estado.style.color = '#dc3545';
        }
    } catch (error) {
        estado.textContent = 'Error de conexión';
        estado.style.color = '#dc3545';
    }
}

async function descubrirEsquema() {
    try {
        const respuesta = await fetch('/api/descubrir-esquema', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const datos = await respuesta.json();
        
        if (datos.estado === 'exito') {
            document.getElementById('tablas-descubiertas').style.display = 'block';
            let html = '<table><tr><th>Tabla</th><th>Columnas</th><th>PK</th><th>FK</th></tr>';
            
            for (const [nombre, info] of Object.entries(datos.tablas)) {
                html += `<tr>
                    <td>${nombre}</td>
                    <td>${info.columnas}</td>
                    <td>${info.claves_primarias.join(', ')}</td>
                    <td>${info.claves_foraneas}</td>
                </tr>`;
            }
            
            html += '</table>';
            document.getElementById('lista-tablas').innerHTML = html;
            alert(`Se encontraron ${datos.num_tablas} tablas en la base de datos origen`);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function crearEstructura() {
    try {
        const respuesta = await fetch('/api/crear-estructura', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const datos = await respuesta.json();
        alert(datos.mensaje);
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function iniciarMigracion() {
    document.getElementById('btn-iniciar').disabled = true;
    document.getElementById('btn-iniciar').textContent = 'Migrando...';
    document.getElementById('btn-pausar').disabled = false;
    
    try {
        const respuesta = await fetch('/api/iniciar-migracion', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const datos = await respuesta.json();
        
        if (datos.estado !== 'exito') {
            alert('Error: ' + datos.mensaje);
            document.getElementById('btn-iniciar').disabled = false;
            document.getElementById('btn-iniciar').textContent = 'Iniciar Migración Completa';
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function pausarMigracion() {
    try {
        await fetch('/api/pausar-migracion', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({proceso_id: 'migracion_1'})
        });
        
        document.getElementById('btn-pausar').disabled = true;
        document.getElementById('btn-iniciar').disabled = false;
        document.getElementById('btn-iniciar').textContent = 'Reanudar Migración';
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Socket.IO para actualizaciones en tiempo real
const socket = io();

socket.on('connect', () => {
    socket.emit('conectar');
});

socket.on('progreso', (datos) => {
    document.getElementById('barra-progreso').style.width = datos.porcentaje + '%';
    document.getElementById('porcentaje').textContent = datos.porcentaje + '%';
    
    if (datos.tabla) {
        document.getElementById('tabla-actual-nombre').textContent = 'Tabla: ' + datos.tabla;
        document.getElementById('barra-tabla').style.width = '50%';
    }
    
    if (datos.metricas) {
        document.getElementById('stat-tablas-ok').textContent = datos.metricas.tablas_ok;
        document.getElementById('stat-extraidos').textContent = datos.metricas.extraidos;
        document.getElementById('stat-cargados').textContent = datos.metricas.cargados;
        document.getElementById('stat-errores').textContent = datos.metricas.errores;
    }
});

socket.on('log', (datos) => {
    const logs = document.getElementById('logs');
    const item = document.createElement('div');
    const hora = new Date().toLocaleTimeString();
    item.textContent = '[' + hora + '] ' + datos.mensaje;
    item.className = 'log-item' + (datos.tipo === 'error' ? ' error' : '');
    logs.appendChild(item);
    logs.scrollTop = logs.scrollHeight;
});

socket.on('migracion_completada', (datos) => {
    document.getElementById('btn-iniciar').disabled = false;
    document.getElementById('btn-iniciar').textContent = 'Iniciar Nueva Migración';
    document.getElementById('btn-pausar').disabled = true;
    alert('Migracion completada!');
});

socket.on('limpiar_interfaz', () => {
    // Resetear barra de progreso
    document.getElementById('barra-progreso').style.width = '0%';
    document.getElementById('porcentaje').textContent = '0%';
    document.getElementById('tabla-actual-nombre').textContent = 'Esperando...';
    document.getElementById('barra-tabla').style.width = '0%';
    
    // Limpiar archivo cargado
    document.getElementById('archivo-cargado').innerHTML = '';
    document.getElementById('tablas-detectadas').style.display = 'none';
    
    // Resetear input de archivo
    if (document.getElementById('archivo')) {
        document.getElementById('archivo').value = '';
    }
    
    // Resetear motor destino
    document.getElementById('motor-destino').value = 'SQLite';
    
    // Resetear estadísticas
    document.getElementById('stat-tablas-ok').textContent = '0';
    document.getElementById('stat-extraidos').textContent = '0';
    document.getElementById('stat-cargados').textContent = '0';
    document.getElementById('stat-errores').textContent = '0';
    
    // Resetear botones
    document.getElementById('btn-iniciar').disabled = true;
    document.getElementById('btn-pausar').disabled = true;
});
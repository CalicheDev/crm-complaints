# CRM Complaints Management System

Un sistema moderno de gestión de quejas para CRM construido con Django REST Framework y React, diseñado para ser escalable, seguro y fácil de usar.

## 🚀 Características

### Para Usuarios
- Registro y autenticación segura de usuarios
- Creación y seguimiento de quejas (incluso de forma anónima)
- Panel personal para visualizar el estado de sus quejas
- Interfaz moderna y responsive

### Para Agentes
- Dashboard para gestionar quejas asignadas
- Sistema de actualización de estado de quejas
- **Gestión de Atenciones:** Registro detallado de contactos con pacientes/clientes
- Seguimiento completo del proceso de resolución
- Vista consolidada de todas las quejas activas

### Para Administradores
- Dashboard analítico completo con métricas en tiempo real
- Gestión completa de usuarios y roles
- Asignación de agentes a quejas
- Estadísticas de rendimiento y resolución

## 🛠️ Tecnologías

### Backend
- **Django 5.1.3** - Framework web robusto
- **Django REST Framework** - API RESTful
- **MySQL** - Base de datos relacional
- **Token Authentication** - Autenticación segura
- **Python Decouple** - Gestión de configuración

### Frontend
- **React 18.3.1** - Librería de interfaz de usuario
- **React Router DOM** - Navegación
- **Tailwind CSS** - Framework de estilos
- **Axios** - Cliente HTTP
- **Context API** - Gestión de estado global

## 📋 Requisitos

- **Python 3.8+**
- **Node.js 16+**
- **MySQL 8.0+**
- **Git**

## ⚡ Instalación Rápida

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd crm-complaints
```

### 2. Configurar el Backend

```bash
# Crear entorno virtual
python -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate

# Instalar dependencias
pip install django djangorestframework django-cors-headers python-decouple mysqlclient

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones de base de datos
```

### 3. Configurar la Base de Datos

```bash
# Crear base de datos MySQL
mysql -u root -p
CREATE DATABASE crm_complaints;
EXIT;

# Ejecutar migraciones
python manage.py migrate

# Crear datos iniciales (grupos y usuario admin)
python manage.py setup_initial_data
```

### 4. Configurar el Frontend

```bash
cd frontend
npm install
```

### 5. Ejecutar la Aplicación

```bash
# Terminal 1: Backend
python manage.py runserver

# Terminal 2: Frontend
cd frontend
npm start
```

La aplicación estará disponible en:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Django Admin:** http://localhost:8000/admin

## 👤 Credenciales por Defecto

Después de ejecutar `setup_initial_data`:
- **Usuario:** admin
- **Contraseña:** admin123
- **Email:** admin@example.com

## 🏗️ Arquitectura

### Backend
```
backend/
├── complaints/          # App principal de quejas
│   ├── models.py       # Modelos: Complaint, Atencion
│   ├── views.py        # Vistas API con endpoints de atenciones
│   ├── serializers.py  # Serialización de datos y atenciones
│   ├── services.py     # Lógica de negocio
│   ├── permissions.py  # Permisos personalizados basados en roles
│   ├── exceptions.py   # Excepciones personalizadas
│   └── admin.py        # Interfaz administrativa
├── users/              # App de gestión de usuarios
│   └── management/     # Comandos personalizados
└── backend/            # Configuración del proyecto
```

### Frontend
```
frontend/src/
├── components/
│   ├── auth/           # Componentes de autenticación
│   ├── common/         # Componentes reutilizables
│   ├── AtencionManager.js # Gestión de atenciones por queja
│   ├── ComplaintDetails.js # Vista detallada con atenciones
│   └── Layout.js       # Layout principal
├── contexts/           # Context API (AuthContext)
├── services/           # Servicios API con endpoints de atenciones
└── App.js             # Componente principal
```

## 🔐 Seguridad

- **Autenticación por tokens** con expiración automática
- **Control de acceso basado en roles** (Admin, Agent, User)
- **Validación exhaustiva** de entrada de datos
- **Rate limiting** para prevenir abuso
- **Cookies seguras** y protección CSRF
- **Logging completo** de eventos de seguridad

## 📊 Roles y Permisos

### Usuario Regular
- Crear quejas
- Ver sus propias quejas
- Actualizar perfil

### Agente
- Ver quejas asignadas
- Actualizar estado de quejas
- **Crear y gestionar atenciones:** Registro de contactos, observaciones y seguimientos
- **Tracking completo:** Múltiples tipos de contacto (teléfono, email, presencial, chat)
- **Resultados de atención:** Contactado, información adicional, seguimiento requerido, etc.
- Gestionar quejas no asignadas

### Administrador
- Acceso completo al sistema
- Dashboard analítico
- Gestión de usuarios y roles
- Asignación de quejas

## 🔧 Configuración de Producción

### Variables de Entorno (.env)
```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_NAME=crm_complaints
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=your_db_host
DATABASE_PORT=3306
CORS_ALLOW_ALL_ORIGINS=False
```

### Comandos de Despliegue
```bash
# Recopilar archivos estáticos
python manage.py collectstatic

# Construir frontend para producción
cd frontend
npm run build
```

## 🎯 Sistema de Atenciones (Nueva Funcionalidad)

### Características Principales
- **Registro Detallado:** Los agentes pueden agregar múltiples observaciones por queja
- **Tipos de Contacto:** Teléfono, Email, Presencial, Chat, Otro
- **Resultados de Atención:**
  - Contactado exitosamente
  - No se pudo contactar
  - Se obtuvo información adicional
  - Requiere seguimiento
  - Resuelto en esta atención

### Flujo de Trabajo
1. **Asignación:** Administrador asigna queja a agente
2. **Primera Atención:** Agente registra primer contacto con observaciones
3. **Seguimientos:** Múltiples atenciones hasta resolución completa
4. **Trazabilidad:** Historial completo de todas las interacciones
5. **Cierre:** Proceso finaliza cuando se resuelve la queja

### Base de Datos
- **Tabla `atenciones`** relacionada con `complaints`
- **Campos principales:** observacion, tipo_contacto, resultado, timestamps
- **Relaciones:** ForeignKey a Complaint y User (agent)

## 📈 Funcionalidades del Dashboard

- **Métricas en Tiempo Real:** Total de quejas, distribución por estado
- **Análisis de Rendimiento:** Tiempo promedio de resolución
- **Carga de Trabajo:** Quejas asignadas por agente
- **Tendencias Mensuales:** Análisis de quejas durante 12 meses
- **Estadísticas de Usuarios:** Distribución de roles y actividad

## 📚 API Endpoints

### Autenticación (`/api/auth/`)
- `POST /register/` - Registro de usuario
- `POST /login/` - Inicio de sesión
- `POST /logout/` - Cierre de sesión
- `GET /profile/` - Obtener perfil de usuario
- `PATCH /profile/` - Actualizar perfil
- `POST /profile/change-password/` - Cambiar contraseña

### Quejas (`/api/complaints/`)
- `GET /` - Listar quejas (filtradas por rol)
- `POST /` - Crear nueva queja
- `GET /{id}/` - Obtener detalles de queja
- `PATCH /{id}/` - Actualizar queja
- `DELETE /{id}/` - Eliminar queja (solo admin)
- `POST /{id}/assign/` - Asignar agente (solo admin)
- `PATCH /{id}/status/` - Actualizar estado
- `GET /my/` - Quejas del usuario actual
- `GET /agent/` - Quejas asignadas al agente
- `GET /dashboard/` - Analíticas del dashboard (solo admin)

### **🆕 Atenciones (`/api/complaints/`)**
- `GET /{complaint_id}/atenciones/` - Listar atenciones de una queja
- `POST /{complaint_id}/atenciones/` - Crear nueva atención
- `GET /atenciones/{id}/` - Obtener atención específica
- `PATCH /atenciones/{id}/` - Actualizar atención
- `DELETE /atenciones/{id}/` - Eliminar atención

### Gestión de Usuarios (Admin) (`/api/auth/users/`)
- `GET /` - Listar usuarios
- `POST /{id}/role/` - Actualizar rol de usuario
- `POST|DELETE /{id}/activation/` - Activar/desactivar usuario
- `GET /statistics/` - Estadísticas de usuarios

## 🧪 Testing

```bash
# Backend tests
python manage.py test

# Frontend tests
cd frontend
npm test

# Comandos de utilidad para testing
python manage.py check_user_roles
python manage.py assign_test_complaint --complaint-id 1 --agent-username test_agent
```

## 🔧 Troubleshooting

### Problemas Comunes

#### Error: "You do not have permission to perform this action"
```bash
# Verificar roles del usuario
python manage.py check_user_roles --username tu_usuario

# Asignar queja a agente para testing
python manage.py assign_test_complaint --complaint-id 1 --agent-username test_agent

# Endpoint de diagnóstico (temporal)
GET /api/complaints/{id}/diagnostic/
```

#### Error: "atenciones.map is not a function"
- **Causa:** Respuesta de API no es un array
- **Solución:** El frontend ahora maneja múltiples formatos de respuesta automáticamente
- **Debug:** Revisar console.log en herramientas de desarrollador

#### Error de Base de Datos
```bash
# Recrear migraciones si es necesario
python manage.py makemigrations
python manage.py migrate

# Verificar conexión a MySQL
python manage.py dbshell
```

#### Problemas de CORS en Desarrollo
```python
# En settings.py, verificar:
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

#### Frontend no se conecta al Backend
1. Verificar que el backend esté ejecutándose en puerto 8000
2. Verificar `REACT_APP_API_URL` en variables de entorno del frontend
3. Revisar Network tab en herramientas de desarrollador

### Comandos de Diagnóstico
```bash
# Verificar estado del sistema
python manage.py check
python manage.py migrate --plan
python manage.py showmigrations

# Logs del servidor
python manage.py runserver --verbosity=2

# Crear usuario de prueba
python manage.py createsuperuser
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Crear un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- Crear un issue en GitHub
- Email: soporte@crmcomplaints.com

---

**CRM Complaints Management System** - Desarrollado con ❤️ para mejorar la gestión de quejas empresariales.
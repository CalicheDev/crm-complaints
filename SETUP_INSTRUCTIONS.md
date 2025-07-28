# Instrucciones de Configuración y Ejecución - CRM Complaints

## ⚠️ Problemas Solucionados

Se han identificado y corregido los siguientes problemas:

### Backend:
1. ✅ Error de sintaxis en `users/services.py` (línea 113)
2. ✅ Configuración de seguridad mejorada
3. ✅ Permisos y serializers implementados
4. ✅ Servicios de lógica de negocio creados

### Frontend:
1. ✅ Componentes faltantes creados
2. ✅ AuthContext implementado
3. ✅ Servicios API centralizados
4. ✅ Componentes comunes reutilizables

## 🚀 Configuración Paso a Paso

### 1. Preparar el Entorno

```bash
# Crear entorno virtual de Python
python -m venv env

# Activar entorno virtual
# En Windows:
env\Scripts\activate
# En macOS/Linux:
source env/bin/activate

# Instalar dependencias del backend
pip install -r requirements.txt
```

### 2. Configurar la Base de Datos

```bash
# Crear base de datos MySQL
mysql -u root -p
CREATE DATABASE crm_complaints CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 3. Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Django Configuration
SECRET_KEY=tu-clave-secreta-aqui-cambiala-en-produccion
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_NAME=crm_complaints
DATABASE_USER=root
DATABASE_PASSWORD=tu_password_mysql
DATABASE_HOST=localhost
DATABASE_PORT=3306

# CORS Configuration (solo para desarrollo)
CORS_ALLOW_ALL_ORIGINS=False
```

### 4. Inicializar el Backend

```bash
# Aplicar migraciones
python manage.py migrate

# Crear datos iniciales (grupos y usuario admin)
python manage.py setup_initial_data

# (Opcional) Crear superuser adicional
python manage.py createsuperuser
```

### 5. Configurar el Frontend

```bash
# Navegar al directorio frontend
cd frontend

# Instalar dependencias
npm install

# Volver al directorio raíz
cd ..
```

## 🏃‍♂️ Ejecutar la Aplicación

### Terminal 1 - Backend:
```bash
# Desde la raíz del proyecto
python manage.py runserver
```
El backend estará disponible en: http://localhost:8000

### Terminal 2 - Frontend:
```bash
# Desde el directorio frontend
cd frontend
npm start
```
El frontend estará disponible en: http://localhost:3000

## 🔑 Credenciales de Acceso

### Usuario Administrador (creado automáticamente):
- **Usuario:** admin
- **Contraseña:** admin123
- **Email:** admin@example.com

## 🌐 Endpoints de la API

### Autenticación:
- `POST /api/auth/register/` - Registro de usuario
- `POST /api/auth/login/` - Inicio de sesión
- `POST /api/auth/logout/` - Cerrar sesión
- `GET /api/auth/profile/` - Obtener perfil
- `PATCH /api/auth/profile/` - Actualizar perfil

### Gestión de Quejas:
- `GET /api/complaints/` - Listar quejas
- `POST /api/complaints/` - Crear queja
- `GET /api/complaints/{id}/` - Obtener queja específica
- `PATCH /api/complaints/{id}/` - Actualizar queja
- `POST /api/complaints/{id}/assign/` - Asignar agente
- `GET /api/complaints/dashboard/` - Analytics (admin)

## 🧪 Probar la Aplicación

1. **Abrir el navegador** en http://localhost:3000
2. **Registrar un nuevo usuario** o usar las credenciales de admin
3. **Crear una queja** desde el formulario
4. **Navegar entre las secciones** según tu rol
5. **Probar funcionalidades** como asignación de agentes (admin)

## 🔧 Solución de Problemas Comunes

### Error: "ModuleNotFoundError"
```bash
# Asegúrate de que el entorno virtual esté activado
pip install -r requirements.txt
```

### Error: "Port already in use"
```bash
# Backend (puerto 8000)
python manage.py runserver 0.0.0.0:8001

# Frontend (puerto 3000)
npm start -- --port 3001
```

### Error de conexión a la base de datos:
1. Verificar que MySQL esté ejecutándose
2. Confirmar credenciales en el archivo `.env`
3. Verificar que la base de datos `crm_complaints` exista

### Problemas con CORS:
- En desarrollo, asegúrate de que `CORS_ALLOW_ALL_ORIGINS=False` en `.env`
- El frontend debe ejecutarse en `localhost:3000`

## 📱 Funcionalidades Disponibles

### Para Usuarios Regulares:
- ✅ Registro y autenticación
- ✅ Crear quejas
- ✅ Ver mis quejas
- ✅ Actualizar perfil

### Para Agentes:
- ✅ Ver quejas asignadas
- ✅ Actualizar estado de quejas
- ✅ Gestionar quejas no asignadas

### Para Administradores:
- ✅ Dashboard analítico completo
- ✅ Gestión de usuarios y roles
- ✅ Asignación de quejas a agentes
- ✅ Vista global de todas las quejas

## 🎯 Próximos Pasos

Una vez que la aplicación esté funcionando:

1. **Personalizar** el diseño según tus necesidades
2. **Configurar** email notifications (opcional)
3. **Implementar** tests automatizados
4. **Desplegar** en producción con las configuraciones adecuadas

## 📞 Soporte

Si encuentras algún problema, revisa:
1. Los logs del servidor Django
2. La consola del navegador para errores de frontend
3. Que todas las dependencias estén instaladas correctamente

¡La aplicación ahora debe ejecutarse correctamente sin errores! 🎉
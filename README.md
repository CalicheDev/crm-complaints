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
│   ├── models.py       # Modelos de datos
│   ├── views.py        # Vistas API
│   ├── serializers.py  # Serialización de datos
│   ├── services.py     # Lógica de negocio
│   ├── permissions.py  # Permisos personalizados
│   └── exceptions.py   # Excepciones personalizadas
├── users/              # App de gestión de usuarios
└── backend/            # Configuración del proyecto
```

### Frontend
```
frontend/src/
├── components/
│   ├── auth/           # Componentes de autenticación
│   ├── common/         # Componentes reutilizables
│   └── Layout.js       # Layout principal
├── contexts/           # Context API (AuthContext)
├── services/           # Servicios API
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

## 📈 Funcionalidades del Dashboard

- **Métricas en Tiempo Real:** Total de quejas, distribución por estado
- **Análisis de Rendimiento:** Tiempo promedio de resolución
- **Carga de Trabajo:** Quejas asignadas por agente
- **Tendencias Mensuales:** Análisis de quejas durante 12 meses
- **Estadísticas de Usuarios:** Distribución de roles y actividad

## 🧪 Testing

```bash
# Backend tests
python manage.py test

# Frontend tests
cd frontend
npm test
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
# Guía de Solución de Problemas - Omnichannel

## Error 403 - Unauthorized

### Problema
Al intentar acceder a `/omnichannel` aparece el error: "403-Unauthorized You don't have permission to access this resource."

### Soluciones

#### 1. Verificar Usuario y Grupos
Asegurate de que tu usuario tenga los permisos correctos:

```bash
# Verificar usuarios y grupos
python manage.py shell -c "
from django.contrib.auth.models import User, Group
for user in User.objects.all():
    groups = list(user.groups.values_list('name', flat=True))
    print(f'{user.username} - Groups: {groups}')
"
```

#### 2. Crear Usuario Admin de Prueba
Si no tienes un usuario con permisos apropiados:

```bash
python manage.py shell -c "
from django.contrib.auth.models import User, Group

# Crear usuario admin
admin_group = Group.objects.get(name='admin')
user, created = User.objects.get_or_create(
    username='omni_admin',
    defaults={
        'email': 'admin@omni.com',
        'first_name': 'Omni',
        'last_name': 'Admin',
    }
)
user.set_password('admin123')
user.save()
user.groups.add(admin_group)
print(f'Usuario creado: {user.username} con grupos: {list(user.groups.values_list(\"name\", flat=True))}')
"
```

#### 3. Crear Usuario Agent de Prueba
Para crear un usuario agente:

```bash
python manage.py shell -c "
from django.contrib.auth.models import User, Group

# Crear usuario agente
agent_group = Group.objects.get(name='agent')
user, created = User.objects.get_or_create(
    username='omni_agent',
    defaults={
        'email': 'agent@omni.com',
        'first_name': 'Omni',
        'last_name': 'Agent',
    }
)
user.set_password('agent123')
user.save()
user.groups.add(agent_group)
print(f'Usuario creado: {user.username} con grupos: {list(user.groups.values_list(\"name\", flat=True))}')
"
```

#### 4. Verificar Configuración de Permisos
La ruta omnichannel requiere que el usuario sea admin O agent. Si el componente `ProtectedRoute` no está funcionando correctamente, la ruta está configurada para permitir cualquier usuario autenticado.

### Datos de Login de Prueba

Una vez creados los usuarios de prueba, puedes usar:

**Admin:**
- Username: `omni_admin`
- Password: `admin123`

**Agent:**
- Username: `omni_agent`
- Password: `agent123`

**Usuarios Existentes:**
- Username: `admin` (si existe)
- Username: `test_agent` (si existe)

## Problemas Comunes de la API

### Error de CORS
Si ves errores de CORS en la consola del navegador:

1. Verificar que el servidor Django esté corriendo en `http://localhost:8000`
2. Verificar que el frontend esté corriendo en `http://localhost:3000`
3. Verificar configuración CORS en `backend/settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### Token de Autenticación
Si hay problemas con el token:

1. Verificar que el token esté almacenado en localStorage:
   ```javascript
   console.log(localStorage.getItem('authToken'));
   console.log(localStorage.getItem('userData'));
   ```

2. Limpiar localStorage si es necesario:
   ```javascript
   localStorage.removeItem('authToken');
   localStorage.removeItem('userData');
   ```

### Verificar API Backend
Probar directamente la API:

```bash
# Obtener token (reemplazar con credenciales reales)
curl -X POST -H "Content-Type: application/json" \
     -d '{"username":"omni_admin","password":"admin123"}' \
     http://localhost:8000/api/auth/login/

# Usar token para acceder a omnichannel (reemplazar TOKEN)
curl -H "Authorization: Token YOUR_TOKEN_HERE" \
     http://localhost:8000/api/omnichannel/conversations/
```

## Inicialización de Datos

Si no hay datos de prueba, ejecutar:

```bash
python manage.py setup_omnichannel_data
```

Este comando creará:
- 8 canales de comunicación
- 6 tags de conversación
- 3 contactos de prueba
- 3 conversaciones con mensajes

## Problemas de Dependencias

### Error con date-fns
Si hay errores relacionados con `date-fns`, verificar instalación:

```bash
cd frontend
npm install date-fns
```

Las importaciones están temporalmente comentadas para evitar errores de compilación. Para reactivarlas:

1. Descomentar imports en:
   - `ConversationList.js`
   - `ConversationView.js`
   - `ContactInteractionHistory.js`

2. Reemplazar:
   ```javascript
   new Date(timestamp).toLocaleString()
   ```
   
   Con:
   ```javascript
   formatDistanceToNow(new Date(timestamp), { addSuffix: true, locale: es })
   ```

## Estructura de Permisos

### Acceso por Rol:
- **Admin**: Acceso completo a todas las funciones
- **Agent**: Acceso a conversaciones asignadas y panel omnichannel
- **User**: Sin acceso al panel omnichannel

### URLs de Acceso:
- `/omnichannel` - Panel principal (Admin/Agent)
- `/api/omnichannel/*` - APIs backend (Admin/Agent)

## Logs de Debug

Para debuggear problemas, añadir logs temporalmente:

```javascript
// En AuthContext.js
const hasRole = (role) => {
  console.log('Checking role:', role, 'User groups:', state.user?.groups);
  if (!state.user || !state.user.groups) return false;
  return state.user.groups.includes(role);
};
```

## Contacto para Soporte

Si los problemas persisten:

1. Verificar logs del servidor Django en la terminal
2. Verificar errores en la consola del navegador (F12 > Console)
3. Verificar network tab para errores de API (F12 > Network)
4. Documentar el error específico y pasos para reproducirlo
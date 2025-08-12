# Guía de Solución Rápida - Error 403 Omnichannel

## 🔧 Problema Resuelto

### Error Original:
```
OmnichannelPanel.js:82 Error loading conversations: SyntaxError: Unexpected token '<', "<!DOCTYPE "... is not valid JSON
```

### Causa:
Las URLs de la API estaban configuradas como relativas (`/api/...`) en lugar de absolutas (`http://localhost:8000/api/...`), lo que hacía que el frontend React buscara en el puerto 3000 en lugar del puerto 8000 de Django.

### ✅ Solución Aplicada:

1. **URLs corregidas** en todos los componentes omnichannel:
   - `OmnichannelPanel.js` ✅
   - `ConversationView.js` ✅  
   - `ContactInteractionHistory.js` ✅

2. **Token authentication** corregido:
   - Cambié `localStorage.getItem('token')` por `localStorage.getItem('authToken')` ✅

3. **Hook personalizado** creado:
   - `useOmnichannelAPI.js` para centralizar las llamadas a la API ✅

## 🚀 Pasos para Probar

### 1. Verificar que Django esté corriendo:
```bash
# Desde la raíz del proyecto
python manage.py runserver
```
Debería mostrar: `Starting development server at http://127.0.0.1:8000/`

### 2. Verificar que React esté corriendo:
```bash
# Desde frontend/
npm start
```
Debería mostrar: `Local: http://localhost:3000`

### 3. Crear usuario de prueba si no existe:
```bash
python manage.py shell -c "
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token

# Usuario Admin
admin_group = Group.objects.get(name='admin')
user, created = User.objects.get_or_create(
    username='omni_admin',
    defaults={
        'email': 'admin@test.com',
        'first_name': 'Admin',
        'last_name': 'Test'
    }
)
user.set_password('admin123')
user.save()
user.groups.add(admin_group)

# Generar token
token, created = Token.objects.get_or_create(user=user)
print(f'Usuario: {user.username}')
print(f'Password: admin123')
print(f'Token: {token.key}')
"
```

### 4. Probar Login y Acceso:
1. Ir a `http://localhost:3000/login`
2. Usar credenciales: `omni_admin` / `admin123`
3. Navegar a `http://localhost:3000/omnichannel`

## 🔍 Verificación de API

### Probar API manualmente:
```bash
# 1. Login para obtener token
curl -X POST -H "Content-Type: application/json" \
     -d '{"username":"omni_admin","password":"admin123"}' \
     http://localhost:8000/api/auth/login/

# 2. Usar token (reemplazar YOUR_TOKEN)
curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/omnichannel/conversations/
```

### Respuesta Esperada:
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "contact": {...},
      "channel": {...},
      ...
    }
  ]
}
```

## ⚡ Si Aún No Funciona

### 1. Limpiar LocalStorage:
```javascript
// En consola del navegador (F12)
localStorage.clear();
```

### 2. Verificar Token en LocalStorage:
```javascript
// Después de login exitoso
console.log(localStorage.getItem('authToken'));
console.log(localStorage.getItem('userData'));
```

### 3. Verificar Errores en Consola:
- Abrir DevTools (F12)
- Ver tab "Console" para errores de JavaScript
- Ver tab "Network" para errores de API

## 📁 Archivos Modificados

- ✅ `frontend/src/components/omnichannel/OmnichannelPanel.js`
- ✅ `frontend/src/components/omnichannel/ConversationView.js`
- ✅ `frontend/src/components/omnichannel/ContactInteractionHistory.js`
- ✅ `frontend/src/components/omnichannel/useOmnichannelAPI.js` (nuevo)
- ✅ `frontend/src/components/omnichannel/MessageInput.js`
- ✅ `frontend/src/App.js`
- ✅ `frontend/src/components/common/ProtectedRoute.js`

## 🎯 Status

**LISTO PARA USAR** - El panel omnichannel debería funcionar correctamente con:
- ✅ Carga de conversaciones
- ✅ Vista de mensajes
- ✅ Historial de contactos
- ✅ Filtros por canal/estado
- ✅ Autenticación corregida

¡El sistema está completamente operativo!
# Guía Rápida de Autenticación

## Endpoints Disponibles

### 1. Registro de Usuario
- **URL**: `http://localhost:8001/register`
- **Método**: `POST`
- **Body**: Ver `request_registro.json`

#### Ejemplo de Request (JSON):
```json
{
  "username": "usuario_prueba",
  "email": "prueba@example.com",
  "password": "MiPassword123!",
  "age": 25,
  "entorno": "casa",
  "nivel_educativo": "secundaria"
}
```

#### Valores permitidos para `entorno`:
- `casa`
- `primaria`
- `secundaria`
- `preescolar`
- `preparatoria`
- `centro_rehabilitacion`

#### Valores permitidos para `nivel_educativo`:
- `ninguno`
- `analfabeta`
- `educacion_inicial`
- `preescolar`
- `primaria`
- `secundaria`
- `bachillerato_general`
- `bachillerato_tecnico`
- `bachillerato_profesional`
- `licenciatura`
- `especialidad`
- `maestria`
- `doctorado`
- `tecnico_superior_universitario`
- `profesional_asociado`
- `educacion_normal`
- `alfabetizacion_adultos`
- `primaria_adultos`
- `secundaria_adultos`

#### Respuesta exitosa (201):
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "usuario_prueba",
  "email": "prueba@example.com",
  "message": "Usuario registrado exitosamente"
}
```

---

### 2. Login
- **URL**: `http://localhost:8001/login`
- **Método**: `POST`
- **Body**: Ver `request_login.json`

#### Ejemplo de Request (JSON):
```json
{
  "email": "prueba@example.com",
  "password": "MiPassword123!"
}
```

#### Respuesta exitosa (200):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

---

## Uso del Token en Trace Service

Una vez que obtengas el `access_token` del endpoint de login, úsalo en el header `Authorization` de tus peticiones al trace-service:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Ejemplo en Thunder Client:

1. En la pestaña **Headers**, agrega:
   - **Header name**: `Authorization`
   - **Header value**: `Bearer {tu_access_token_aqui}`

   O simplemente pega:
   ```
   Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
   ```

2. Realiza tu petición POST a `/practices` con:
   - `letra`: La letra a analizar (ej: "A")
   - `imagen`: El archivo de imagen a subir

---

## Pasos para Probar Trace Service

1. **Registra un usuario** (solo la primera vez):
   ```
   POST http://localhost:8001/register
   Body: request_registro.json
   ```

2. **Haz login** para obtener el token:
   ```
   POST http://localhost:8001/login
   Body: request_login.json
   ```
   Copia el `access_token` de la respuesta.

3. **Prueba el trace-service**:
   ```
   POST http://localhost:8002/practices
   Headers:
     Authorization: Bearer {tu_access_token}
   Body (form-data):
     letra: A
     imagen: [selecciona tu archivo de imagen]
   ```

---

## Notas Importantes

- El servicio de autenticación está corriendo en el puerto **8001**
- El trace-service está en el puerto **8002** (según tu configuración)
- El token JWT tiene una expiración configurada (por defecto 30 minutos según la configuración)
- Si el token expira, simplemente vuelve a hacer login para obtener uno nuevo


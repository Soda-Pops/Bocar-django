# Plan de Implementación — Módulo IA

## Objetivo

Proteger el panel de reentrenamiento para que **solo usuarios con rol Sistemas (`IT`)** puedan acceder.
El flujo completo es: pantalla de login propia del módulo → validación de credenciales → verificación de rol → acceso al panel.

---

## Contexto del proyecto (leer antes de empezar)

El proyecto ya tiene toda la infraestructura de autenticación construida. No hay que reinventar nada:

- **Modelo de usuario:** `users.models.CustomUser` — extiende `AbstractUser`. El campo relevante es `role`, que puede ser `'IT'` (Sistemas), `'Com'`, `'Ind'`, `'Pro'` o `'SinRol'`.
- **Autenticación:** JWT via cookies HttpOnly. El token se llama `access_token` y viaja en cookie, no en header.
- **Clase de autenticación:** `users.authentication.CookieJWTAuthentication` — ya lee el token de la cookie automáticamente.
- **Permiso existente para Sistemas:** `users.permissions.IsSistemas` — ya verifica `role == 'IT'`. **Reutilizarlo.**
- **Endpoints de auth ya existentes:**
  - `POST /auth/login/` → recibe `email` y `password`, devuelve cookies JWT + datos del usuario (`role`, `is_admin`, etc.)
  - `POST /auth/logout/` → invalida el token y borra las cookies
  - `GET /auth/me/` → devuelve los datos del usuario autenticado si la cookie es válida; 401 si no

---

## Flujo que debe implementarse

```
Usuario visita /modulo-ia/
        |
        ¿Tiene cookie access_token válida con role='IT'?
       /                                                \
      NO                                               SÍ
      |                                                 |
Redirigir a                                    Mostrar panel de
/modulo-ia/login/                              reentrenamiento
      |
Usuario llena email + password
      |
POST a /auth/login/ (endpoint existente)
      |
     ¿OK?
    /     \
  NO       SÍ
  |         |
Mostrar    ¿role == 'IT'?
error      /           \
          NO            SÍ
          |              |
   Hacer logout    Redirigir a
   inmediato y     /modulo-ia/
   mostrar         (panel protegido)
   "Acceso
   denegado"
```

---

## Pasos de implementación

### Paso 1 — Crear la vista y URL del login del módulo

Crear una nueva vista Django (basada en template, como la vista existente) en `modulo_IA/views.py` para la pantalla de login.

- URL sugerida: `/modulo-ia/login/`
- Nombre de URL sugerido: `modulo-ia-login`
- Debe aceptar GET (mostrar el formulario) y POST (enviar credenciales).

### Paso 2 — Crear el template de login

Crear `modulo_IA/templates/modulo_ia/login.html` con un formulario simple de email y contraseña.

- El formulario debe enviar POST con CSRF token (ya es práctica del proyecto — ver el template existente `panel_reentrenamiento.html`).
- Mostrar mensajes de error cuando las credenciales sean incorrectas o el rol no sea `IT`.
- Seguir el estilo visual del template existente (mismo navbar "BOCAR | Sistemas", misma paleta de colores).

### Paso 3 — Implementar la lógica del login en la vista

Dentro del handler POST de la vista de login, el desarrollador necesita:

1. Leer `email` y `password` del formulario.
2. Llamar a `django.contrib.auth.authenticate(request, email=email, password=password)` — esto devuelve el usuario si las credenciales son válidas, o `None` si no.
3. Si la autenticación falla → renderizar el template con un mensaje de error.
4. Si la autenticación es exitosa → verificar que `user.role == 'IT'`.
5. Si el rol no es `IT` → renderizar el template con el mensaje "Acceso denegado: se requiere rol Sistemas."
6. Si el rol es `IT` → generar los tokens JWT y setear las cookies, luego redirigir a `/modulo-ia/`.
   - Para generar los tokens: `from rest_framework_simplejwt.tokens import RefreshToken` → `RefreshToken.for_user(user)`.
   - Para setear las cookies: seguir exactamente el mismo patrón que `users/views.py` → `LoginView.post()`. Copiar los parámetros de las cookies (`httponly`, `secure`, `samesite`, `max_age`) desde ahí para mantener consistencia.

### Paso 4 — Crear un decorador o mixin de protección para vistas de template

El proyecto usa JWT en cookies, no sesiones Django, por lo que `@login_required` de Django **no funciona aquí**.

Es necesario crear un decorador personalizado (en `modulo_IA/` o en `users/`) que:

1. Lea la cookie `access_token` de la request.
2. Si no existe → redirigir a `/modulo-ia/login/`.
3. Si existe → validarla usando `CookieJWTAuthentication` o directamente con `rest_framework_simplejwt`.
4. Si el token expiró o es inválido → redirigir a `/modulo-ia/login/`.
5. Si el token es válido → verificar que el usuario tenga `role == 'IT'`.
6. Si el rol no es `IT` → redirigir a `/modulo-ia/login/` con un parámetro de error, o a una página de acceso denegado.
7. Si todo es correcto → dejar pasar la request a la vista original.

Aplicar este decorador a la vista `panel_reentrenamiento` existente.

### Paso 5 — Agregar opción de logout en el panel

El template `panel_reentrenamiento.html` debe incluir un botón o enlace de "Cerrar sesión".

- Al hacer clic, enviar POST a `/auth/logout/` (endpoint existente).
- Después del logout, redirigir a `/modulo-ia/login/`.

### Paso 6 — Registrar las nuevas URLs

En `modulo_IA/urls.py`, agregar la ruta para la vista de login creada en el Paso 1.

---

## Recomendaciones importantes

**Sobre seguridad:**
- No reimplementar la generación de tokens — copiar el patrón exacto de `users/views.py → LoginView` para que las cookies tengan los mismos parámetros de seguridad que el resto del sistema.
- No guardar el rol en una variable de sesión ni en localStorage. El rol siempre debe leerse del token validado o llamando a `GET /auth/me/`.
- El decorador del Paso 4 es la pieza más crítica — asegurarse de que la validación del token sea real (no solo verificar que la cookie exista).

**Sobre consistencia con el resto del proyecto:**
- La clase `IsSistemas` de `users/permissions.py` ya existe y tiene la lógica de verificación de rol. El decorador del Paso 4 puede inspirarse en ella o reutilizar su lógica internamente.
- El modelo a usar siempre es `users.models.CustomUser`. El rol de Sistemas es el string `'IT'` (no `'Sistemas'` ni `'IT_ROLE'`).
- Mantener el estilo visual de los templates existentes.

**Sobre lo que aún no está implementado:**
- El botón "Reentrenar modelo" actualmente solo muestra un mensaje. La lógica real de reentrenamiento (Celery, llamada a modelo, etc.) queda pendiente y es independiente de este flujo de autenticación.

---

## Archivos que se deben tocar

| Archivo | Acción |
|---|---|
| `modulo_IA/views.py` | Agregar vista de login; agregar decorador de protección a `panel_reentrenamiento` |
| `modulo_IA/urls.py` | Registrar la URL del login |
| `modulo_IA/templates/modulo_ia/login.html` | Crear template del formulario de login |
| `modulo_IA/templates/modulo_ia/panel_reentrenamiento.html` | Agregar botón de logout |
| `users/permissions.py` *(opcional)* | Si se crea un decorador genérico reutilizable, puede vivir aquí |

---

## Lo que NO hay que crear

- Nuevos endpoints de API — el login del módulo es una vista de template, no un endpoint REST.
- Nuevos modelos de usuario ni nuevos roles — el rol `IT` ya existe.
- Un sistema de sesiones paralelo — usar los mismos tokens JWT del sistema.
- Lógica de refresh automático de tokens — no es necesaria para este módulo.

# Laboratorio IAM: Keycloak con Federación de Google OAuth 2.0 y Aplicación Python

---

## Requisitos Previos

- **Docker** y **Docker Compose**
- **Python 3.10+
- Cuenta activa en **Google Cloud Console**

---

## Guía de Despliegue e Instalación

### 1. Iniciar la infraestructura de Keycloak
Desde la raíz del proyecto, ejecuta:
```bash
docker compose up -d
```
Keycloak estará disponible en `http://localhost:8080`. La consola de administración se encuentra en `http://localhost:8080/admin`.

### 2. Configurar la Aplicación Python (Flask)
Ingresa a la carpeta `app/` e instala las dependencias:
```bash
cd app
pip install -r requirements.txt
```

### 3. Ejecutar la Aplicación
```bash
python3 app.py
```
La aplicación cliente estará escuchando en `http://localhost:3000`.

---

## Verificación del Flujo de Autenticación

1. Navegar a `http://localhost:3000`.
2. Hacer clic en **Iniciar Sesión con Keycloak**.
3. En la pantalla de autenticación de Keycloak, seleccionar el proveedor **Google**
4. Tras validar credenciales en Google, serás redirigido a `http://localhost:3000/callback`.
5. La aplicación intercambiará el código por el ID Token JWT y mostrará los datos de perfil y roles.
6. Hacer clic en **Cerrar Sesión** para probar el Single Logout (SLO).

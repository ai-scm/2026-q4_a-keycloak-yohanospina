import os
import requests
import jwt
from flask import Flask, redirect, request, session, url_for, render_template_string

app = Flask(__name__)
app.secret_key = "super-secret-key-para-sesiones-flask"

# Configuración de Keycloak
KEYCLOAK_URL = "http://localhost:8080"
REALM_NAME = "semillero-realm"
CLIENT_ID = "dummy-app-client"

# REEMPLAZA ESTE VALOR POR TU CLIENT SECRET COPIADO EN EL PASO 2:
CLIENT_SECRET = "WTKggVgR3o5ZzPEKJ97sqriCSOxV1LGD"
REDIRECT_URI = "http://localhost:3000/callback"

AUTH_URL = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/auth"
TOKEN_URL = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token"
LOGOUT_URL = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/logout"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Aplicación Dummy Keycloak</title>
</head>
<body>
    <h1>🔒 Aplicación Dummy en Python (Flask)</h1>
    {% if user %}
        <p>¡Bienvenido, {{ user.get('name', user.get('preferred_username', 'Usuario')) }}! 👋</p>
        <p><strong>Email:</strong> {{ user.get('email', 'No provisto') }}</p>
        <p><strong>Roles asignados:</strong> {{ roles }}</p>
        <p><strong>Datos del Token (ID Token decoded):</strong></p>
        <pre>{{ user_json }}</pre>
        <br>
        <a href="/logout"><button>Cerrar Sesión</button></a>
    {% else %}
        <p>No has iniciado sesión. Autentícate mediante Keycloak.</p>
        <a href="/login"><button>Iniciar Sesión con Keycloak</button></a>
    {% endif %}
</body>
</html>
"""

@app.route("/")
def index():
    user = session.get("user")
    roles = session.get("roles", [])
    import json
    user_json = json.dumps(user, indent=2) if user else ""
    return render_template_string(HTML_TEMPLATE, user=user, roles=roles, user_json=user_json)

@app.route("/login")
def login():
    login_url = f"{AUTH_URL}?client_id={CLIENT_ID}&response_type=code&scope=openid%20profile%20email&redirect_uri={REDIRECT_URI}"
    return redirect(login_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Error: No se recibió el código de autorización.", 400

    # Intercambiar el código por tokens
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code != 200:
        return f"Error al obtener token: {response.text}", 400

    tokens = response.json()
    id_token = tokens.get("id_token")
    access_token = tokens.get("access_token")

    # Decodificar el ID Token (sin verificación de firma estricta para simplificar la prueba local)
    decoded_user = jwt.decode(id_token, options={"verify_signature": False})
    decoded_access = jwt.decode(access_token, options={"verify_signature": False})

    # Extraer roles del Realm
    realm_access = decoded_access.get("realm_access", {})
    roles = realm_access.get("roles", [])

    session["user"] = decoded_user
    session["roles"] = roles
    session["id_token"] = id_token

    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    id_token = session.get("id_token")
    session.clear()
    if id_token:
        end_session_url = f"{LOGOUT_URL}?post_logout_redirect_uri=http://localhost:3000/&id_token_hint={id_token}"
        return redirect(end_session_url)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
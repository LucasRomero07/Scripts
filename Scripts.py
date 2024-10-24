import http.server
import socketserver
import json
import random
import string
import time

PORT = 5000
EXPIRATION_TIME = 4 * 60 * 60  # 4 horas en segundos

# Almacén de contraseñas temporales con sus tiempos de expiración
temporary_data = {}

# Función para generar una contraseña temporal
def generate_temp_password():
    return ''.join(random.choices(string.digits, k=4))  # Contraseña de 4 dígitos numéricos

# Función para generar un nombre de usuario temporal
def generate_temp_username():
    return 'user_' + ''.join(random.choices(string.ascii_letters + string.digits, k=8))  # Usuario aleatorio de 8 caracteres

# Clase para manejar las solicitudes HTTP
class MyRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        # Obtener la longitud del contenido y leer los datos recibidos
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            # Parsear el cuerpo de la solicitud como JSON
            data = json.loads(post_data)
            username = data.get('username', None)
            
            if not username:
                # Si no se proporciona un nombre de usuario, enviar error 400
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error": "No username provided"}')
                return
            
            # Generar la contraseña temporal y establecer el tiempo de expiración
            temp_password = generate_temp_password()
            temp_username = generate_temp_username()
            expiration_time = time.time() + EXPIRATION_TIME  # Expira en 4 horas
            
            # Guardar la contraseña temporal y su expiración en el diccionario
            temporary_data[username] = {'PASS_TEMP': temp_password, 'TEMP_USERNAME': temp_username, 'expires_at': expiration_time}
            
            # Enviar la respuesta con la contraseña temporal y el usuario temporal
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({"TEMP_USERNAME": temp_username, "PASS_TEMP": temp_password})
            self.wfile.write(response.encode())
        
        except json.JSONDecodeError:
            # Si el JSON no está en el formato correcto, enviar error 400
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"error": "Invalid JSON format"}')

# Iniciar el servidor
with socketserver.TCPServer(("", PORT), MyRequestHandler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
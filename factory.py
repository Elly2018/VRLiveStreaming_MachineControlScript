import requests
import threading
import socket

class AJA_Control:
    def __init__(self, ip_address):
        self.ip_address = ip_address

    def connect(self, input, output):
        url = "http://"
        url += self.ip_address
        url += "/config?action=set&config=0&paramid=eParamID_XPT_Destination"
        url += str(output)
        url += "_Status&value="
        url += str(input)
        response = requests.get(url)
        return response

class Hyperdeck8K_Control:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
    def start_recording(self):
        threading.Thread(target=self._start_recording).start()
    def _start_recording(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip_address, self.port))
            s.sendall(b"record\n")
            response = s.recv(1024)
            print("Received", repr(response))
    def stop_recording(self):
        threading.Thread(target=self._stop_recording).start()
    def _stop_recording(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip_address, self.port))
            s.sendall(b"stop\n")
            response = s.recv(1024)
            print("Received", repr(response))

class HyperdeckHD_Control:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
    def start_recording(self):
        threading.Thread(target=self._start_recording).start()
    def _start_recording(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip_address, self.port))
            s.sendall(b"record\n")
            response = s.recv(1024)
            print("Received", repr(response))
    def stop_recording(self):
        threading.Thread(target=self._stop_recording).start()
    def _stop_recording(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip_address, self.port))
            s.sendall(b"stop\n")
            response = s.recv(1024)
            print("Received", repr(response))

class ControlScriptFactory:
    def __init__(self):
        pass

    def create_aja_control(self, ip_address):
        return AJA_Control(ip_address)
    
    def create_hyperdeck8K_control(self, ip_address, port):
        return Hyperdeck8K_Control(ip_address, port)

    def create_hyperdeckHD_control(self, ip_address, port):
        return HyperdeckHD_Control(ip_address, port)
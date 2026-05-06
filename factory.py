import requests

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
    def __init__(self, ip_address):
        self.ip_address = ip_address
    def start_recording(self):
        pass
    def stop_recording(self):
        pass

class HyperdeckHD_Control:
    def __init__(self, ip_address):
        self.ip_address = ip_address
    def start_recording(self):
        pass
    def stop_recording(self):
        pass

class ControlScriptFactory:
    def __init__(self):
        pass

    def create_aja_control(self, ip_address):
        return AJA_Control(ip_address)
    
    def create_hyperdeck8K_control(self, ip_address):
        return Hyperdeck8K_Control(ip_address)

    def create_hyperdeckHD_control(self, ip_address):
        return HyperdeckHD_Control(ip_address)
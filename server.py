from http.server import BaseHTTPRequestHandler,  HTTPServer
from collections import namedtuple
import socket
import os
import threading
import json
import cgi
import time

IP = socket.gethostbyname(socket.gethostname())

Device = namedtuple('Device',['ip','port'])

DEVICE_NAME_IP_MAPPING = {
    "Device1": Device(ip="192.168.0.19", port=9001),
    "Device2": Device(ip="192.168.0.19", port=9002),
    "Device3": Device(ip="192.168.0.19", port=9003),
    "Device4": Device(ip="192.168.0.19", port=9004)
}

HEADER_LEN = 16
ENCODING_FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "DISCONNECT"

class DeviceSocketHandler:
    def __init__(self,device_name,):
        self.device_name = device_name

    def parse_details(self):
        device_details = DEVICE_NAME_IP_MAPPING[self.device_name]
        device_ip = device_details.ip
        device_port = device_details.port
        return device_ip,device_port

    def establish_sock_conn(self):
        device_addrs = self.parse_details()    

        print(f"Connecting to {device_addrs}")
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.connect(device_addrs)
        print("Connection successful....")
        return client

    # def test_sock(self):
    #     conn = self.establish_sock_conn()
    #     msg = "This is a test message"
    #     msg_len = len(msg)
    #     header_len = 16
    #     enc_format = 'utf-8'
    #     encoded_msg = msg.encode(ENCODING_FORMAT)
    #     header_msg = str(msg_len).encode(ENCODING_FORMAT)+b" "*(header_len-len(str(msg_len)))
    #     print(header_msg)
    #     conn.send(header_msg)
    #     conn.send(encoded_msg)
    #     resp = conn.recv(1024).decode(ENCODING_FORMAT)
    #     time.sleep(10)




class ClientHTTPHandler(BaseHTTPRequestHandler):
    def _set_headers(self,resp=200,content='application/json'):
        self.send_response(200)
        self.send_header('Content-type', content)
        self.end_headers()

    def encode_message(self, message):
        message = message+" "+DISCONNECT_MESSAGE
        msg_len = len(message)
        encoded_msg = message.encode(ENCODING_FORMAT)
        header_msg = str(msg_len).encode(ENCODING_FORMAT)+b" "*(HEADER_LEN-len(str(msg_len)))
        return header_msg, encoded_msg


    def handle_post(self, data):
        sock_handler = DeviceSocketHandler(data['device_name'])
        conn = sock_handler.establish_sock_conn()
        message = data['message']
        header_msg, encoded_msg = self.encode_message(message)
        conn.send(header_msg)
        conn.send(encoded_msg)
        resp = conn.recv(1024).decode(ENCODING_FORMAT)
        conn.close()
        return resp

        

    def do_GET(self):
        base_dir = r'e:\Python\ClientServer\HTTP'
        try:
            if self.path.endswith('.html'):
                file_path = os.path.join(base_dir,self.path)
                with open(file_path,'rb') as fl:
                    data = fl.read()
                content_type='text/html'
            
            elif self.path.endswith('.json'):
                file_path = os.path.join(base_dir,self.path)
                with open(file_path,'r') as fl:
                    data = json.loads(fl.read())
                
                data = bytes(json.dumps(data),'utf-8')
                content_type='application/json'
            else:
                data = bytes(json.dumps({'name': 'Hello World', 'received': 'ok'}),'utf-8')
                print("HERE")
                content_type='application/json'
                
            self._set_headers(content_type)
            self.wfile.write(data)
            return

        except IOError:
            self.send_error(404,'Requested file Not found')

        except Exception as e:
            self.send_error(500,str(e))

    def do_POST(self):
        try:
            ctype, _ = cgi.parse_header(self.headers.get('content-type'))
            
            # refuse to receive non-json content
            if ctype != 'application/json':
                self.send_response(400)
                self.end_headers()
                return
                
            length = int(self.headers.get('content-length'))
            data = json.loads(json.loads(self.rfile.read(length).decode('utf-8')))
            resp = self.handle_post(data)
            data['device_response']=resp

            # send the message back
            self._set_headers()
            self.wfile.write(bytes(json.dumps(data),'utf-8'))
            return
        except Exception as e:
            self.send_error(500,str(e))


def main():
    IP = socket.gethostbyname(socket.gethostname())
    PORT = 9998
    ADDRS = (IP,PORT)
    print(type(IP))

    print(f"Staring HTTP server on {IP}:{PORT}")
    httpd = HTTPServer(ADDRS,ClientHTTPHandler)
    print("HTTP server running successfully...... ")
    httpd.serve_forever()

    # sock_handler = DeviceSocketHandler("Device1")
    # sock_handler.test_sock()

if __name__=='__main__':
    main()
    #pass

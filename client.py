from  http import client
import sys
import json

SERVER_IP = sys.argv[1]
SERVER_PORT = sys.argv[2]
RESOURCE_NAME = "test.html"

conn = client.HTTPConnection(SERVER_IP,SERVER_PORT)

while 1:
    cmd = input("Input request command: (Eg: GET test.html)")
    cmd = cmd.split()

    if cmd[0]=='GET':
        if len(cmd) != 2:
            conn.request(cmd[0],"")
        else:
            conn.request(cmd[0],cmd[1])
        resp = conn.getresponse()

        print(resp.status,resp.reason)
        resp_data = resp.read()
        print(resp_data)

    elif cmd[0] == 'POST':
        if len(cmd) != 3:
            raise Exception("POST requires the endpoint and the json file. Eg: POST /post test.json")
        else:
            post_cmd, endpoint, src = cmd[0], cmd[1], cmd[2]
            if not src.endswith('.json'):
                raise Exception("The source file to be posted must be a JSON file")
            with open(src,'r') as fl:
                data = fl.read()
            json_data = json.dumps(data)
            req_header = {'Content-type': 'application/json'}
            conn.request(post_cmd,endpoint,json_data,req_header)

            resp = conn.getresponse()
            resp_data = resp.read()
            print(resp_data)

    elif cmd[0]=='EXIT':
        print("Exiting the client....")
        break
    else:
        print("Incorrect Request Entered.\n Allowed options are 'GET' and 'POST'")
        break

conn.close()
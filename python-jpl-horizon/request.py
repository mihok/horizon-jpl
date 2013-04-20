#!/usr/bin/python

# python-jpl-horizon
#
# Written by: Siddarth Kalra (@siddarthkalra)

import sys
import json

import SimpleHTTPServer
import SocketServer
from BaseHTTPServer import BaseHTTPRequestHandler

from jpl.horizon import Horizon
import urllib

class JplRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if "/api?query=" in self.path:
            json_obj = self.__get_query_json(self.path)
            if json_obj is None:
                self.__send_http_response_400("Invalid json provided.")
                return
            
            #validate the json request 
            json_validation = self.__is_json_obj_valid(json_obj)
            print json_validation
            
            if not json_validation["success"]:
                self.__send_http_response_400(json_validation["message"])
            else:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
            
                json_obj = json_obj["horizons-api"]
                response = {
                    "version": None
                }
                
                #initialize horizon
                horizon_data = Horizon()
                response["version"] = horizon_data.version()
                
                if json_obj["query_type"] == "list" and "filters" in json_obj:
                    if json_obj["filters"]["body_type"] == "mb":
                        response["mb"] = horizon_data.major() 
                    elif json_obj["filters"]["body_type"] == "sb":
                        response["sb"] = horizon_data.minor()
                elif json_obj["query_type"] == "id" and "filters" in json_obj and "value" in json_obj["filters"]:
                    id = json_obj["filters"]["value"]
                    
                    if id.isdigit():
                        response["id"] = horizon_data.get(id)
            
                #do the JSON magic
                json.dump(response, self.wfile)

    def __send_http_response_400(self, message):
        self.send_response(400)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(message)        

    def __get_query_json(self, path):
        json_str = urllib.unquote_plus(path[11:])
        print json_str

        try:
            return json.loads(json_str)
        except:
            return None

    def __is_json_obj_valid(self, json_obj):
        required_keys = ("version", "response_type", "query_type", "filters")
        query_types = ("id", "name")
        body_types = ("mb", "sb")
        response_types = ("json")

        result = {"success": False, "message": "Failed to validate request."}

        if not "horizons-api" in json_obj:
            result["message"] = "Failed. First level key 'horizons-api' missing."
            return result

        for r_key in required_keys:
            if not r_key in json_obj["horizons-api"]:
                result["message"] = "Failed. Second level key '%s' missing." % r_key
                return result

        result["success"] = True
        result["message"] = "Success"
        return result


if sys.argv[1:]:
    port = int(sys.argv[1])
else:
    port = 8000
server_address = ('127.0.0.1', port)

httpd = SocketServer.TCPServer(server_address, JplRequestHandler)

print "serving at port", port
httpd.serve_forever()


# if __name__ == "__main__":
#     # params = cgi.FieldStorage()
#     # json = get_query_json(params)

#     if json is None:
#         print "Invalid json structure."
#         sys.exit()

#     json_validation = is_json_obj_valid(json)

#     if not json_validation["success"]:
#         print '''HTTP/1.1 501 Not Implemented
#         Content-type: text/html

#         '''
#         sys.exit()

#     #load json into
#     print('Content-type: application/json\r\n\r')
#     print "Start Horizon<br/>"
#     #horizon_data = Horizon()
#     #print horizon.version()

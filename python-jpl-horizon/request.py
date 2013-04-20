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

    JSON_QUERY_PARAM_START_INDEX = 11

    def do_GET(self):
        if self.path[:self.JSON_QUERY_PARAM_START_INDEX] == "/api?query=":
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
                json_obj = json_obj["horizons-api"]
                response = {
                    "version": None
                }
                
                #initialize horizon
                horizon_data = Horizon()
                response["version"] = horizon_data.version()
                
                #decision tree for what horizon method to run
                if json_obj["query_type"] == "list":
                    if json_obj["filters"]["body_type"] == "mb":
                        response["mb"] = horizon_data.major() 
                    elif json_obj["filters"]["body_type"] == "sb":
                        response["sb"] = horizon_data.minor()
                elif json_obj["query_type"] == "id":
                    response["id"] = horizon_data.get(json_obj["filters"]["value"])
                elif json_obj["query_type"] == "name": 
                    response["name"] = horizon_data.get(json_obj["filters"]["value"])
            
                #set success headers
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                
                #do the JSON magic
                json.dump(response, self.wfile)


    "send back a bad request header with a message"
    def __send_http_response_400(self, message):
        self.send_response(400)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(message)        

    "read the url path and load the JSON"
    def __get_query_json(self, path):
        json_str = urllib.unquote_plus(path[self.JSON_QUERY_PARAM_START_INDEX:])
        print json_str

        try:
            return json.loads(json_str)
        except:
            return None

    "validate the json request object"
    def __is_json_obj_valid(self, json_obj):
        required_keys = ("version", "response_type", "query_type", "filters")
        query_types = ("id", "name", "list") #to be used
        list_body_types = ("mb", "sb") #to be used
        response_types = ("json") #to be used

        result = {"success": False, "message": "Failed to validate request."}

        if not "horizons-api" in json_obj:
            result["message"] = "Failed. First level key 'horizons-api' missing."
            return result

        for r_key in required_keys:
            if not r_key in json_obj["horizons-api"]:
                result["message"] = "Failed. Second level key '%s' missing." % r_key
                return result

         #TODO -- more in-depth json query validation
         #if json_obj["horizons-api"]["query_type"] == "list":
         #elif json_obj["horizons-api"]["query_type"] == "id":
         #elif json_obj["horizons-api"]["query_type"] == "name":

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

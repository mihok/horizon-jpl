# python-jpl-horizon
#
# Written by: Siddarth Kalra (@siddarthkalra)
#
# The MIT License (MIT)
# Copyright (c) 2013
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the
# following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import sys
import json
from os import curdir, sep

import SimpleHTTPServer
import SocketServer
from BaseHTTPServer import BaseHTTPRequestHandler

from horizon.interface import Interface
import urllib
import re

class JplRequestHandler(BaseHTTPRequestHandler):
        
    #TODO -- more convenience API
    #by enum and name --> planet, asteroid, spacecraft, moon --> .get(name, enum)
    #by name --> .get(name)
        
    def do_GET(self):
    
        print "PATH: " + self.path
        
        #determine the request type being received
        req_info = self.__get_request_info(self.path)
        if req_info["type"] is None:
            self.__send_http_response_400("Invalid request type.")
            return
        
        response = {
            "version": None
        }        
    
        if req_info["type"] == "id_req":
            #initialize horizon
            horizon_data = Interface()
            response["version"] = horizon_data.version()
                        
            if req_info["params"] is None or len(req_info["params"]) == 0:
                self.__send_http_response_400("Invalid request, no body id specified.")
                return
            elif not req_info["params"].isdigit():
                self.__send_http_response_400("Invalid request, body id must be an integer.")
                return
            
            response["body_id"] = horizon_data.get(req_info["params"])
            
            #set success headers
            self.__send_http_response_200("application/json")
                
            #do the JSON magic
            json.dump({"horizons-api": response}, self.wfile)
        elif req_info["type"] == "name_req":
            #initialize horizon
            horizon_data = Horizon()
            response["version"] = horizon_data.version()
                        
            if req_info["params"] is None or len(req_info["params"]) == 0:
                self.__send_http_response_400("Invalid request, no body name specified.")
                return
            
            response["body_name"] = horizon_data.get(req_info["params"])
            
            #set success headers
            self.__send_http_response_200("application/json")
                
            #do the JSON magic
            json.dump({"horizons-api": response}, self.wfile)
        elif req_info["type"] == "list_req":
            #initialize horizon
            horizon_data = Horizon()
            response["version"] = horizon_data.version()
                        
            if req_info["params"] is None or len(req_info["params"]) == 0:
                self.__send_http_response_400("Invalid request, no list type specified.")
                return
            elif req_info["params"] != "mb" and req_info["params"] != "sb":
                self.__send_http_response_400("Invalid request, only mb or sb lists are supported.")
                return
            
            if req_info["params"] == "mb":
                response["mb"] = horizon_data.major()
            elif req_info["params"] == "sb":
                response["mb"] = horizon_data.minor()
            
            #set success headers
            self.__send_http_response_200("application/json")
                
            #do the JSON magic
            json.dump({"horizons-api": response}, self.wfile)      
        elif req_info["type"] == "complex_req":
            json_obj = self.__get_complex_query_json(self.path)
            
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
                
                #initialize horizon
                horizon_data = Horizon()
                response["version"] = horizon_data.version()
                
                #decision tree for what horizon method to run
                if json_obj["query_type"] == "list":
                    if json_obj["filters"]["body_type"] == "mb":
                        response["mb"] = horizon_data.major() 
                    elif json_obj["filters"]["body_type"] == "sb":
                        response["sb"] = horizon_data.minor()
                elif json_obj["query_type"] == "body_id":
                    response["body_id"] = horizon_data.get(json_obj["filters"]["value"])
                elif json_obj["query_type"] == "body_name": 
                    response["body_name"] = horizon_data.get(json_obj["filters"]["value"])
            
                #set success headers
                self.__send_http_response_200("application/json")
                
                #do the JSON magic
                json.dump({"horizons-api": response}, self.wfile)
        elif req_info["type"] == "demo_req":
            f = open("/data/web/nasa.api.niewma.com/python-jpl-horizon/demo/index.html")
            #note that this potentially makes every file on your computer readable by the internet

            self.__send_http_response_200("text/html")
            self.wfile.write(f.read())
            f.close()
        else:
            f = open("/data/web/nasa.api.niewma.com/python-jpl-horizon/demo/" + self.path)
            self.send_response(200)
            self.send_header('Content-type',    'text/javascript')
            self.end_headers()

        # elif req_info["type"] == "file_req":
        #     f = open(curdir + sep + "demo" + self.path)
        #     self.__send_http_response_200("text/html")

            self.wfile.write(f.read())
            f.close()
            
        return
        
    #PRIVATE methods

    "determine the request type being received"
    def __get_request_info(self, path):
        demo_request = re.compile("^\/$")
        file_request = re.compile("^\/(.+)\.{1}[a-z]+$")
        id_request = re.compile("^\/api\?body_id=(.*)$")
        name_request = re.compile("^\/api\?body_name=(.*)$")
        list_request = re.compile("^\/api\?list=(.*)$")
        query_request = re.compile("^\/api\?query=(.*)$")
        
        request_info = {
            "params": None,
            "type": None 
        }
        
        matches = file_request.search(path)
        
        if matches is not None:
            request_info["type"] = "file_req"
            
            return request_info
        
        matches = demo_request.search(path)
        
        if matches is not None:
            request_info["type"] = "demo_req"
            
            return request_info
                    
        matches = query_request.search(path)
        
        if matches is not None:
            query_json = matches.groups()[0]
            request_info["params"] = query_json
            request_info["type"] = "complex_req"
            
            return request_info
        
        matches = id_request.search(path)
        
        if matches is not None:
            id = matches.groups()[0]
            request_info["params"] = id
            request_info["type"] = "id_req"
            
            return request_info
        
        matches = name_request.search(path)
        
        if matches is not None:
            name = matches.groups()[0]
            request_info["params"] = name
            request_info["type"] = "name_req"
            
            return request_info
        
        matches = list_request.search(path)
        
        if matches is not None:
            list_value = matches.groups()[0]
            request_info["params"] = list_value
            request_info["type"] = "list_req"
            
            return request_info
        
        return request_info

    def __send_http_response_200(self, content_type):
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()

    "send back a bad request header with a message"
    def __send_http_response_400(self, message):
        self.send_response(400)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(message)        

    "read the url path and load the JSON for a complex"
    def __get_complex_query_json(self, path):
        json_str = urllib.unquote_plus(path[11:])
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

         #TODO -- more in-depth JSON query validation
         #if json_obj["horizons-api"]["query_type"] == "list":
         #elif json_obj["horizons-api"]["query_type"] == "id":
         #elif json_obj["horizons-api"]["query_type"] == "name":

        result["success"] = True
        result["message"] = "Success"
        return result

#HTTP server related code
if sys.argv[1:]:
    port = int(sys.argv[1])
else:
    port = 8000
server_address = ('127.0.0.1', port)

httpd = SocketServer.TCPServer(server_address, JplRequestHandler)

print "serving at port", port
httpd.serve_forever()

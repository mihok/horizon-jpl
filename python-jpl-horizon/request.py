#!/usr/bin/python

# python-jpl-horizon
#
# Written by: Siddarth Kalra (@siddarthkalra)

import sys
import json

import SimpleHTTPServer
import SocketServer
from BaseHTTPServer import BaseHTTPRequestHandler

# import json
# import cgi, cgitb
from jpl.horizon import Horizon


class JplRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/api":
            self.send_response(200)
            #send headers:
            self.send_header("Content-type", "application/json")
            # send a blank line to end headers:
            self.wfile.write("\n")

            #send response:
            json.dump({'success': True}, self.wfile)


def get_query_json(params):
    if params is None:
        return None
    elif not params["query"]:
        return None

    try:
        return json.loads(params["query"].value)
    except:
        return None


def is_json_obj_valid(json_obj):
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

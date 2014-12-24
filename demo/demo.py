from flask import Flask, render_template, request

from horizon.interface import Interface as Horizon

import json

app = Flask(__name__)

@app.route("/")
def default():
    return render_template('default.html',
         url=request.url,
         title='Horizon JPL Demo'
      )


@app.route("/list/")
def list_default():
    return "/list/"

@app.route("/list/<type>")
def list(type):
    horizon = Horizon()
    result = {
      'version': horizon.get_version(),
      'type': type,
      'data': []
    }
    if (type == 'major'):
        result['data'] = horizon.get_major()
    elif (type == 'minor'):
        result['data'] = horizon.get_minor()

    return json.dumps(result), 200, {'Content-Type': 'application/json; charset=utf-8'}


@app.route("/body/")
def body_default():
  return "/body/"

@app.route("/body/<query>")
def body(query):
  horizon = Horizon()
  result = {
    'version': horizon.get_version(),
    'type': 'body',
    'data': horizon.get(query)
  }
  return json.dumps(result), 200, {'Content-Type': 'application/json; charset=utf-8'}


if __name__ == "__main__":
    app.run(debug=True)

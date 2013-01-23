from flask import Flask, url_for, request, json
app = Flask(__name__)

@app.route('/')
def api_root():
    return 'Welcome'

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods = ['GET', 'POST', 'PATCH', 'PUT', 'DELETE'])
def api_echo(path):
    ret = "Request method: " + request.method
    ret += "\nContent-Type: " + request.headers['Content-Type']
    if request.headers['Content-Type'] == 'application/json':
        ret += "\nMessage: " + json.dumps(request.json)
    else:
        ret += "\nMessage: " + request.data
    print ret
    return ret

if __name__ == '__main__':
    app.run()


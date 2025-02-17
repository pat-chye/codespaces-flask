from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='static')

@app.route('/')
def home():
    return app.send_static_file('index.html')

# Optional: Serve service worker at root
@app.route('/service-worker.js')
def service_worker():
    response = app.send_static_file('service-worker.js')
    response.headers['Content-Type'] = 'application/javascript'
    return response

# Optional: Serve manifest at root
@app.route('/manifest.json')
def manifest():
    return app.send_static_file('manifest.json')

if __name__ == '__main__':
    app.run(debug=True)
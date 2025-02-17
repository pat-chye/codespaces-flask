from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='static')

@app.route('/')
def home():
    # Return the static index.html for the root path
    return app.send_static_file('index.html')

@app.route('/index.html')
def index_page():
    # Return index.html if the browser (or service worker) requests /index.html
    return app.send_static_file('index.html')

@app.route('/service-worker.js')
def service_worker():
    # Serve the service worker at the root
    response = send_from_directory(app.static_folder, 'service-worker.js')
    response.headers['Content-Type'] = 'application/javascript'
    return response

@app.route('/manifest.json')
def manifest():
    # Serve the manifest at the root
    return app.send_static_file('manifest.json')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
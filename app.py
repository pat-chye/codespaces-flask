from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='static')

# 1) Serve the main page from /static/index.html
@app.route('/')
def home():
    return app.send_static_file('index.html')

# 2) Serve the service worker at the root
@app.route('/service-worker.js')
def service_worker():
    response = app.send_static_file('service-worker.js')
    response.headers['Content-Type'] = 'application/javascript'
    return response

if __name__ == '__main__':
    # Running on localhost:5000 by default
    app.run(debug=True, host='0.0.0.0', port=5000)
from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

@app.route('/')
def index():
    return '''
    <h1>Task Manager</h1>
    <p>Welcome to your Task Manager application!</p>
    <p>Status: Running successfully on DigitalOcean</p>
    '''

@app.route('/health')
def health():
    return {'status': 'healthy', 'message': 'Application is running'}

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

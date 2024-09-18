from flask import Flask, render_template, request, send_from_directory, jsonify, redirect, url_for
import os
import json
import socket
import threading
from datetime import datetime

app = Flask(__name__)

static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

storage_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'storage')
if not os.path.exists(storage_folder):
    os.makedirs(storage_folder)

data_file = os.path.join(storage_folder, 'data.json')

if not os.path.exists(data_file):
    with open(data_file, 'w') as f:
        json.dump({}, f)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/message.html', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form.get('username')
        message = request.form.get('message')

        send_message_to_socket_server(username, message)
        
        return redirect(url_for('index'))
    
    return render_template('message.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(static_folder, filename)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404


def send_message_to_socket_server(username, message):
    udp_ip = '127.0.0.1'  
    udp_port = 5000        

    message_data = {
        "username": username,
        "message": message
    }

    message_bytes = json.dumps(message_data).encode('utf-8')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message_bytes, (udp_ip, udp_port))


def start_socket_server():
    udp_ip = '127.0.0.1'
    udp_port = 5000

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((udp_ip, udp_port))

    print(f"Socket сервер працює на {udp_ip}:{udp_port}")

    while True:
        data, addr = sock.recvfrom(1024)
        message_data = json.loads(data.decode('utf-8'))

        timestamp = str(datetime.now())
        with open(data_file, 'r+') as f:
            file_data = json.load(f)
            file_data[timestamp] = message_data
            f.seek(0)
            json.dump(file_data, f, indent=4)


if __name__ == '__main__':
    socket_thread = threading.Thread(target=start_socket_server)
    socket_thread.start()

    app.run(port=3000)

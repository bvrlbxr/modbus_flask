from flask import Flask, render_template, request, jsonify
from pymodbus.client import ModbusTcpClient
from flask_socketio import SocketIO, emit
import eventlet
import time

eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app)

client = ModbusTcpClient('localhost')

def read_modbus():
    while True:
        try:
            print('Reading coils...')
            response = client.read_coils(0, 10)
            if not response.isError():
                data = response.bits
                socketio.emit('modbus_data', {'coils': data, 'error': False})
            else:
                socketio.emit('modbus_data', {'coils': [], 'error': True})

            print('Reading holding registers...')
            response = client.read_holding_registers(0, 10)
            if not response.isError():
                data = response.registers
                socketio.emit('holding_registers_data', {'registers': data, 'error': False})
            else:
                socketio.emit('holding_registers_data', {'registers': [], 'error': True})
        except Exception as e:
            print(f"Exception: {e}")
            socketio.emit('modbus_data', {'coils': [], 'error': True})
            socketio.emit('holding_registers_data', {'registers': [], 'error': True})
        finally:
            time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/write_coil', methods=['POST'])
def write_coil():
    data = request.get_json()
    address = data.get('address')
    value = data.get('value')
    response = client.write_coil(address, value)
    if response.isError():
        return jsonify({'error': 'Failed to write coil'}), 500
    return jsonify({'success': True})

@app.route('/write_register', methods=['POST'])
def write_register():
    data = request.get_json()
    address = data.get('address')
    value = data.get('value')
    response = client.write_register(address, value)
    if response.isError():
        return jsonify({'error': 'Failed to write register'}), 500
    return jsonify({'success': True})

if __name__ == '__main__':
    socketio.start_background_task(target=read_modbus)
    socketio.run(app, debug=True)

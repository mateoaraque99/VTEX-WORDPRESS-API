from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    print(f"Content-Type received: {request.content_type}")  # Verifica el tipo de contenido

    if request.content_type == 'application/json':  # Si el contenido es JSON
        data = request.get_json()
        print("Received JSON data:", data)
        return jsonify({'status': 'success'}), 200
    elif request.content_type == 'application/x-www-form-urlencoded':  # Si es form-urlencoded
        data = request.form
        print("Received form data:", data)
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'error': 'Unsupported Media Type'}), 415  # Error si no soporta el formato

if __name__ == '__main__':
    app.run(port=5000)
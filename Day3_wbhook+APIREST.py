from flask import Flask, request, jsonify
import requests
import pandas as pd

app = Flask(__name__)

# Configuración de las APIs
url_woocommerce = 'https://staging20.tiendasparadox.co/wp-json/wc/v3/products'
consumer_key = 'ck_44c351e1e064192b1c0f61ef95eb798e03a04f4f'
consumer_secret = 'cs_e677de55ee418c0b0a2d43e55780b88a3c24bc3c'

url_dakota = 'https://dakota2.co/wp-json/wc/v3/products'
consumer_key_dakota = 'ck_01a22ae321cae062b8eae9c4be1363fb69db61ff'
consumer_secret_dakota = 'cs_c17d71cf95dc17eb7c83fefdbe34a2ffc2be6607'

@app.route('/webhook', methods=['POST'])
def webhook():
    print(f"Content-Type received: {request.content_type}")

    if request.content_type == 'application/json':  # Si el contenido es JSON
        data = request.get_json()
        print("Received JSON data:", data)
    elif request.content_type == 'application/x-www-form-urlencoded':  # Si es form-urlencoded
        data = request.form
        print("Received form data:", data)
    else:
        return jsonify({'error': 'Unsupported Media Type'}), 415  # Error si no soporta el formato

    # Aquí puedes procesar el producto recibido
    # Por ejemplo, si estás buscando un producto específico como 'Dummy'
    product_name = data.get('name')  # Ajusta esto según los datos que recibas

    # Hacer la petición GET para obtener los productos
    response = requests.get(url_woocommerce, auth=(consumer_key, consumer_secret))
    if response.status_code == 200:
        products = response.json()

        # Extraer solo el producto que coincida con el nombre recibido
        product_data = None
        for product in products:
            if product.get('name') == product_name:
                product_data = {
                    'name': product.get('name'),
                    'description': product.get('description'),
                    'regular_price': str(product.get('price')),
                    'stock_quantity': product.get('stock_quantity'),
                    'status': 'publish',
                    'type': 'simple',
                }
                break

        # Guardar el producto en formato CSV y JSON
        if product_data:
            df = pd.DataFrame([product_data])
            df.to_csv('dummy_product.csv', index=False)
            df.to_json('dummy_product.json', orient='records', lines=True)
            print(df.head())

            # Hacer la petición POST para crear el producto en Dakota
            response_dakota = requests.post(url_dakota, json=product_data, auth=(consumer_key_dakota, consumer_secret_dakota))

            if response_dakota.status_code == 201:
                print("Producto creado exitosamente en Dakota 2")
                print(response_dakota.json())
            else:
                print(f"Error al crear el producto en Dakota 2: {response_dakota.status_code}")
                print(response_dakota.text)
        else:
            print(f"Producto '{product_name}' no encontrado.")
    else:
        print(f"Error al obtener productos de WooCommerce: {response.status_code}")

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(port=5000)
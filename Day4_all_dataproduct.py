from flask import Flask, request, jsonify
import requests
import pandas as pd

print("Procesando..")

app = Flask(__name__)

# Configuración de las APIs
url_woocommerce = 'https://staging20.tiendasparadox.co/wp-json/wc/v3/products'
consumer_key = 'ck_44c351e1e064192b1c0f61ef95eb798e03a04f4f'
consumer_secret = 'cs_e677de55ee418c0b0a2d43e55780b88a3c24bc3c'

url_dakota = 'https://dakota2.co/wp-json/wc/v3/products'
consumer_key_dakota = 'ck_01a22ae321cae062b8eae9c4be1363fb69db61ff'
consumer_secret_dakota = 'cs_c17d71cf95dc17eb7c83fefdbe34a2ffc2be6607'

@app.route('/webhook-product-created', methods=['POST'])
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
               
            # Extraer la primera imagen y el resto si aplica
                images = product.get('images', [])
            # Convertir la lista de imágenes en un solo string separado por comas, si existen múltiples imágenes
                image_urls = ",".join([image['src'] for image in images]) if images else None

                # Construimos el diccionario del producto
                
                product_data = {
                    'name': product.get('name'),
                    'description': product.get('description'),
                    'short_description': product.get('short_description'),
                    'regular_price': str(product.get('price')),
                    'manage_stock': True,  # Habilitar la gestión de stock
                    'stock_quantity': product.get('stock_quantity', 0),  # Cantidad de stock
                    'status': 'publish',
                    'type': 'simple',
                    # Agregar las imágenes como un string si existen
                    'images': [{'src': url} for url in image_urls.split(',')] if image_urls else []
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

@app.route('/webhook-product-update', methods=['POST'])
def webhook_product_update():
    print(f"Received update webhook: {request.content_type}")
    if request.content_type == 'application/json':
        data = request.get_json()
        print("Received JSON data:", data)

        # Extraer el ID del producto
        product_id = data.get('id')
        if product_id:
            # Obtener los detalles del producto actualizado
            product_url = f'{url_woocommerce}/{product_id}'
            response = requests.get(product_url, auth=(consumer_key, consumer_secret))
            if response.status_code == 200:
                product = response.json()
                product_data = {
                    'name': product.get('name'),
                    'description': product.get('description'),
                    'short_description': product.get('short_description'),
                    'regular_price': str(product.get('regular_price')),
                    'stock_quantity': product.get('stock_quantity'),
                    'status': product.get('status'),
                    'type': product.get('type'),
                    'images': [{'src': img['src']} for img in product.get('images', [])]
                }

                # Actualizar el producto en Dakota
                response_dakota = requests.put(f'{url_dakota}/{product_id}', json=product_data, auth=(consumer_key_dakota, consumer_secret_dakota))
                if response_dakota.status_code == 200:
                    print("Producto actualizado exitosamente en Dakota")
                    return jsonify({'status': 'success', 'message': 'Producto actualizado en Dakota'}), 200
                else:
                    print(f"Error al actualizar el producto en Dakota: {response_dakota.status_code}")
                    return jsonify({'status': 'error', 'message': response_dakota.text}), response_dakota.status_code
            else:
                print(f"Error al obtener el producto de WooCommerce: {response.status_code}")
                return jsonify({'status': 'error', 'message': 'Producto no encontrado en WooCommerce'}), 404
        else:
            print("Product ID no encontrado en la notificación.")
            return jsonify({'status': 'error', 'message': 'Product ID no encontrado'}), 400
    else:
        return jsonify({'error': 'Unsupported Media Type'}), 415


if __name__ == '__main__':
    app.run(port=5000)
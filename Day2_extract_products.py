import requests
import pandas as pd

# URL de la API de productos
url = 'https://staging20.tiendasparadox.co/wp-json/wc/v3/products'
consumer_key = 'ck_44c351e1e064192b1c0f61ef95eb798e03a04f4f'
consumer_secret = 'cs_e677de55ee418c0b0a2d43e55780b88a3c24bc3c'

# Hacer la petición GET para obtener los productos
response = requests.get(url, auth=(consumer_key, consumer_secret))

# Verificamos si la respuesta fue exitosa
if response.status_code == 200:
    # Convertimos la respuesta a formato JSON
    products = response.json()

    # Extraer solo el producto con nombre 'Dummy'
    product_data = None  # Inicializamos como None
    for product in products:
        if product.get('name') == 'Dummy':
            product_data = {
                'name': product.get('name'),
                'description': product.get('description'),
                'regular_price': str(product.get('price')),  # Convertir a string
                'stock_quantity': product.get('stock_quantity'),
                'status': 'publish',  # Asegúrate de incluir otros campos necesarios
                'type': 'simple',
            }
            break  # Salir del bucle una vez que encontramos el producto

    # Convertir a DataFrame de Pandas solo si se encontró el producto 'Dummy'
    if product_data:
        df = pd.DataFrame([product_data])  # Usar una lista para crear un DataFrame

        # Guardar el DataFrame en formato CSV
        df.to_csv('dummy_product.csv', index=False)
        
        # Guardar el DataFrame en formato JSON
        df.to_json('dummy_product.json', orient='records', lines=True)

        # Imprimir los datos del producto 'Dummy'
        print(df.head())
        
        # Ahora proceder a insertar en Dakota 2
        url_dakota = 'https://dakota2.co/wp-json/wc/v3/products'
        consumer_key_dakota = 'ck_01a22ae321cae062b8eae9c4be1363fb69db61ff'
        consumer_secret_dakota = 'cs_c17d71cf95dc17eb7c83fefdbe34a2ffc2be6607'
        
        # Hacer la petición POST para crear el producto en Dakota 2
        response_dakota = requests.post(url_dakota, json=product_data, auth=(consumer_key_dakota, consumer_secret_dakota))

        if response_dakota.status_code == 201:
            print("Producto creado exitosamente en Dakota 2")
            print(response_dakota.json())  # Imprimir los detalles del nuevo producto
        else:
            print(f"Error al crear el producto en Dakota 2: {response_dakota.status_code}")
            print(response_dakota.text)
    else:
        print("Producto 'Dummy' no encontrado.")
else:
    print(f"Error: {response.status_code}")

# Mostrar la lista de productos extraídos
print(product_data)
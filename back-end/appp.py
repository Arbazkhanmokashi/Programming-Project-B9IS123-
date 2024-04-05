from flask import Flask, jsonify, request

app = Flask(__name__)

products = [ 
     {"id": 1, "name": "Product 1", "quantity": 10},
     {"id": 2, "name": "Product 2", "quantity": 20},
     {"id": 3, "name": "Product 3", "quantity": 30}
]
@app.route('/')
def home_page():
    return 'This is the Home Page'
    
@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(products)

@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = next((product for product in products if product['id'] == id), None)
    if product:
        return jsonify(product)
    return jsonify({"message": "Product not found"}), 404

@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    if 'name' in data and 'quantity' in data:
        new_product = {
            "id": len(products) + 1,
            "name": data['name'],
            "quantity": data['quantity']
        }
        products.append(new_product)
        return jsonify({"message": "Product added successfully"}), 201
    return jsonify({"message": "Missing data (name or quantity)"}), 400

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.get_json()
    product = next((product for product in products if product['id'] == id), None)
    if product:
        product['name'] = data.get('name', product['name'])
        product['quantity'] = data.get('quantity', product['quantity'])
        return jsonify({"message": "Product updated successfully"})
    return jsonify({"message": "Product not found"}), 404

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    global products
    products = [product for product in products if product['id'] != id]
    return jsonify({"message": "Product deleted successfully"})

if __name__ == '__main__':
    app.run(debug=True)

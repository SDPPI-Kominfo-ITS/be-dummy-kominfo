from flask import Flask, jsonify, request, render_template
import json
import os
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app, methods=["GET", "POST", "PUT", "DELETE"])

DATA_FILE = 'data.json'
USERS_FILE = 'users.json'

def read_json_file(filename):
    if not os.path.exists(filename):
        return {}
    with open(filename, 'r') as file:
        return json.load(file)
    
def write_json_file(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

@app.route('/')
def documentation():
    return render_template('documentation.html')

@app.route('/signup', methods=['POST'])
def signup():
    users = read_json_file(USERS_FILE)
    data = request.json

    if data is None:
        return {"error": "Invalid JSON"}, 400
    
    Email = data.get('Email')
    Password = data.get('Password')

    print(users)

    for i in users:
        print(i['Email'])

    if any(user['Email'] == Email for user in users):
        return jsonify({
            'message':'User alreadey exists!'
        }), 400
    
    users.append(data)
    write_json_file(USERS_FILE, users)
    return jsonify({
        'message':'User created succesfully!',
        'Email' : Email,
        'Password' : Password
    }), 200

@app.route('/login', methods=['POST'])  # Perbaiki 'method' menjadi 'methods'
def login():
    users = read_json_file(USERS_FILE)
    data = request.json

    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400
    
    Email = data.get("Email")
    Password = data.get("Password")

    for user in users:
        if user["Email"] == Email and user["Password"] == Password:
            return jsonify({"success": True, "message": "Login successful"}), 200  # Mengembalikan JSON yang jelas
        
    return jsonify({"error": "Invalid email or password", "success": False}), 400  # Konsisten dalam response JSON

@app.route('/add', methods=['POST'])
def add_data():
    data = request.json

    if data is None or "Title" not in data:
        return jsonify({"error": "Invalid JSON, 'Title' is required"}), 400
    
    existing_data = read_json_file(DATA_FILE)
    # existing_data = existing_data['data']

    new_id = max([item['ID'] for item in existing_data['data']], default=0) + 1
    new_entry = {
        "ID": new_id,
        "CreatedAt": datetime.utcnow().isoformat() + 'Z',
        "UpdatedAt": datetime.utcnow().isoformat() + 'Z',
        "DeletedAt": None,
        "Title": data["Title"],
        "Body": []
    }

    existing_data['data'].append(new_entry)
    write_json_file(DATA_FILE, existing_data)

    return jsonify({"success":True, "data": new_entry}), 200

@app.route('/add',methods=['GET'])
def get_all_data():
    file_data = read_json_file(DATA_FILE)
    return jsonify(file_data), 200

@app.route('/data/<dataName>/body', methods=['GET'])
def get_data_body(dataName):
    # Baca data dari file JSON
    file_data = read_json_file(DATA_FILE)

    # Loop untuk mencari item berdasarkan dataName (Title)
    for item in file_data['data']:
        if item['Title'] == dataName:
            # Kembalikan Body dalam format JSON
            return jsonify(item['Body']), 200
    
    # Jika data dengan Title tidak ditemukan
    return jsonify({"error": "Data not found"}), 404

@app.route('/add/<dataName>/body', methods=['POST'])
def add_data_body(dataName):
    file_data = read_json_file(DATA_FILE)

    data = request.json

    if data is None or "Body" not in data:
        return jsonify({"error": "Invalid JSON, 'Body' is required"}), 400

    for item in file_data["data"]:
        if item["Title"] == dataName:
            item['Body'].append(data['Body'])

            write_json_file(DATA_FILE, file_data)
            return jsonify({"success": True, "Body": item["Body"]}), 200
    return jsonify({"error": "Data not found"}), 404

@app.route('/data/<dataName>/body/<int:index>', methods=['PUT'])
def edit_data_body(dataName, index):
    file_data = read_json_file(DATA_FILE)
    data = request.json
    if data is None or "Body" not in data:
        return jsonify({"error": "Invalid JSON, 'Body' is required"}), 400
    
    new_data = data['Body']

    for item in file_data['data']:
        if item['Title'] == dataName:
            if index < 0 or index >= len(item['Body']):
                return jsonify({'error':'Index out of range'}), 400
            
            item['Body'][index] = new_data

            write_json_file(DATA_FILE, file_data)
            return jsonify({'success':True,'Body': item['Body']}), 200
    
    return jsonify({"error": "Data not found"}), 404

@app.route('/data/<dataName>/body/<int:index>', methods=['DELETE'])
def delete_data_body(dataName, index):
    file_data = read_json_file(DATA_FILE)

    # Loop through the data to find the matching Title
    for item in file_data['data']:
        if item['Title'] == dataName:
            # Check if the index is valid
            if index < 0 or index >= len(item['Body']):
                return jsonify({'error': 'Index out of range'}), 400
            
            # Remove the item at the given index
            deleted_item = item['Body'].pop(index)
            
            # Save the updated data back to the file
            write_json_file(DATA_FILE, file_data)
            
            # Return the remaining body after deletion
            return jsonify({'success': True, 'Body': item['Body']}), 200
    
    # If no data with the given title is found
    return jsonify({"error": "Data not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
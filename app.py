from flask import Flask, request, jsonify
import os
import uuid
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# Carregar as credenciais do Firebase a partir das variáveis de ambiente
cred_obj = {
    "type": os.environ["type"],
    "project_id": os.environ["project_id"],
    "private_key_id": os.environ["private_key_id"],
    "private_key": os.environ["private_key"].replace('\\n', '\n'),
    "client_email": os.environ["client_email"],
    "client_id": os.environ["client_id"],
    "auth_uri": os.environ["auth_uri"],
    "token_uri": os.environ["token_uri"],
    "auth_provider_x509_cert_url": os.environ["auth_provider_x509_cert_url"],
    "client_x509_cert_url": os.environ["client_x509_cert_url"]
}

cred = credentials.Certificate(cred_obj)
firebase_admin.initialize_app(cred, {'databaseURL': os.environ['firebase_url']})

@app.route('/create', methods=['POST'])
def create_record():
    unique_id = str(uuid.uuid4())
    request_data = request.get_json()

    data = {
        "email": request_data['email'],
        "numero": request_data['numero'],
        "greendados": request_data['link'],
        "situacao": "pago",
        "idTelegram": ""
    }

    ref = db.reference('/')
    ref.child(unique_id).set(data)

    return jsonify({"success": True, "id": unique_id}), 201

@app.route('/read/<numero>', methods=['GET'])
def read_record(numero):
    ref = db.reference('/')
    registros = ref.get()

    # Vamos garantir que a comparação seja feita como número
    try:
        numero = int(numero)  # Convertendo a string da URL para inteiro
    except ValueError:
        return jsonify({"error": "O número fornecido não é válido"}), 400

    # Encontrar todos os registros com o número correspondente
    matching_records = {k: v for k, v in registros.items() if v.get('numero') == numero}

    if matching_records:
        return jsonify(matching_records), 200
    else:
        return jsonify({"error": "Nenhum registro encontrado para o número fornecido"}), 404

@app.route('/')
def hello_world():
    return 'Hello, World!'

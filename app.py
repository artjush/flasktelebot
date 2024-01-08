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
        "gp1": request_data['link'],
        "gp2": "",
        "gp3": "",
        "expira": request_data['expira'],
        "idTelegram": ""
    }

    ref = db.reference('/')
    ref.child(unique_id).set(data)

    return jsonify({"success": True, "id": unique_id}), 201

@app.route('/read/<numero>', methods=['GET'])
def read_record(numero):
    try:
        # Assegurar que o número é um inteiro
        numero = int(numero)
    except ValueError:
        # Se o número não for inteiro, retorne um erro
        return jsonify({"error": "Número fornecido inválido"}), 400

    ref = db.reference('/')
    # Buscar na base de dados por registros que tenham o campo 'numero' igual ao valor especificado
    query = ref.order_by_child('numero').equal_to(numero).get()

    if query:
        return jsonify(query), 200
    else:
        return jsonify({"error": "Nenhum registro encontrado para o número fornecido"}), 404

@app.route('/')
def hello_world():
    return 'Hello, World!'

import os
import uuid
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, jsonify, request

app = Flask(__name__)

# Carregar as credenciais do Firebase a partir das variáveis de ambiente
cred_obj = {
    "type": os.environ["ype"],
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
firebase_admin.initialize_app(cred,
                              {'databaseURL': os.environ['firebase_url']})


@app.route('/create', methods=['POST'])
def create_record():
  try:
    # Gera um identificador único
    unique_id = str(uuid.uuid4())

    # Obtém dados do corpo da solicitação
    request_data = request.get_json()

    # Prepara os dados para inserção
    data = {
        "email": request_data['email'],
        "numero": request_data['numero'],
        "link": request_data['link'],
        "situacao": "pago",
        "idTelegram": ""
    }

    # Insere os dados no Firebase Realtime Database
    ref = db.reference('/')
    ref.child(unique_id).set(data)

    return jsonify({"success": True, "id": unique_id}), 201

  except Exception as e:
    print("An internal error occurred: {}".format(e))
    return "An internal error occurred", 500


@app.route('/')
def hello_world():
  return 'Hello, World!'


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)

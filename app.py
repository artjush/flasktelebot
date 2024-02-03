from flask import Flask, request, jsonify
import os
import uuid
import firebase_admin
from firebase_admin import credentials, db
import requests

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
        "gp4": "",
        "expira": request_data['expira'],
        "idTelegram": ""
    }

    ref = db.reference('/')
    ref.child(unique_id).set(data)

    return jsonify({"success": True, "id": unique_id}), 201

@app.route('/read/<path:identificador>', methods=['GET'])
def read_record(identificador):
    try:
        # Tentar converter o identificador para int
        numero = int(identificador)
        # Se a conversão for bem-sucedida, trate como um número
        return read_by_number(numero)
    except ValueError:
        # Se a conversão falhar, trate como uma string
        return read_by_string(identificador)

def read_by_number(numero):
    ref = db.reference('/')
    query = ref.order_by_child('numero').equal_to(numero).get()

    if query:
        return jsonify(query), 200
    else:
        return jsonify({"error": "Nenhum registro encontrado para o número fornecido"}), 404

def read_by_string(identificador):
    ref = db.reference('/')
    # Suponha que 'nome' é um campo válido para busca por string
    query = ref.order_by_child('email').equal_to(identificador).get()

    if query:
        return jsonify(query), 200
    else:
        return jsonify({"error": "Nenhum registro encontrado para o identificador fornecido"}), 404

@app.route('/revoke_invite_gp1', methods=['POST'])
def revoke_invite():
    try:
        # Dados necessários para a chamada da API
        bot_token = '6877266169:AAEu_8S4FGh80M6XSFFq3gjJYY7zI06tb1I'
        chat_id = '-1002046964190'
        invite_link = request.json.get('invite_link')

        # URL da API do Telegram para revogar um link de convite
        url = f'https://api.telegram.org/bot{bot_token}/revokeChatInviteLink'

        # Dados para enviar com o POST request
        payload = {
            'chat_id': chat_id,
            'invite_link': invite_link
        }

        # Fazendo a chamada da API
        response = requests.post(url, data=payload)
        return jsonify(response.json()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/revoke_invite_gp2', methods=['POST'])
def revoke_invite2():
    try:
        # Dados necessários para a chamada da API
        bot_token = '6877266169:AAEu_8S4FGh80M6XSFFq3gjJYY7zI06tb1I'
        chat_id = '-1002087905925'
        invite_link = request.json.get('invite_link')

        # URL da API do Telegram para revogar um link de convite
        url = f'https://api.telegram.org/bot{bot_token}/revokeChatInviteLink'

        # Dados para enviar com o POST request
        payload = {
            'chat_id': chat_id,
            'invite_link': invite_link
        }

        # Fazendo a chamada da API
        response = requests.post(url, data=payload)
        return jsonify(response.json()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/revoke_invite_gp3', methods=['POST'])
def revoke_invite3():
    try:
        # Dados necessários para a chamada da API
        bot_token = '6877266169:AAEu_8S4FGh80M6XSFFq3gjJYY7zI06tb1I'
        chat_id = '-1001699690132'
        invite_link = request.json.get('invite_link')

        # URL da API do Telegram para revogar um link de convite
        url = f'https://api.telegram.org/bot{bot_token}/revokeChatInviteLink'

        # Dados para enviar com o POST request
        payload = {
            'chat_id': chat_id,
            'invite_link': invite_link
        }

        # Fazendo a chamada da API
        response = requests.post(url, data=payload)
        return jsonify(response.json()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/revoke_invite_gp4', methods=['POST'])
def revoke_invite_gp4():
    try:
        # Dados necessários para a chamada da API
        bot_token = '6877266169:AAEu_8S4FGh80M6XSFFq3gjJYY7zI06tb1I'
        chat_id = '-1001989430689'
        invite_link = request.json.get('invite_link')

        # URL da API do Telegram para revogar um link de convite
        url = f'https://api.telegram.org/bot{bot_token}/revokeChatInviteLink'

        # Dados para enviar com o POST request
        payload = {
            'chat_id': chat_id,
            'invite_link': invite_link
        }

        # Fazendo a chamada da API
        response = requests.post(url, data=payload)
        return jsonify(response.json()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update_expiry/<numero>', methods=['POST'])
def update_expiry(numero):
    try:
        numero = int(numero)
        nova_data = request.json.get('expira')

        ref = db.reference('/')
        query_result = ref.order_by_child('numero').equal_to(numero).get()

        if query_result:
            for key in query_result:
                ref.child(key).update({"expira": nova_data})
                return jsonify({"success": True, "message": "Data de expiração atualizada"}), 200
        else:
            return jsonify({"error": "Número não encontrado"}), 404

    except ValueError:
        return jsonify({"error": "Número fornecido inválido"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete_record', methods=['POST'])
def delete_record():
    try:
        numero = request.json.get('numero')
        
        # Certifique-se que o 'numero' é um inteiro
        numero = int(numero)
        
        # Query para encontrar o registro com o número correspondente
        ref = db.reference('/')
        query_result = ref.order_by_child('numero').equal_to(numero).get()
        
        # Se um registro com o número correspondente for encontrado, delete-o
        if query_result:
            for key in query_result:
                ref.child(key).delete()
                return jsonify({"success": True, "message": "Registro deletado com sucesso"}), 200
        
        # Se nenhum registro for encontrado com o número fornecido
        return jsonify({"error": "Nenhum registro encontrado com o número fornecido"}), 404
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update_groups/<numero>', methods=['POST'])
def update_groups(numero):
    try:
        numero = int(numero)
        dados_atualizados = request.json.get('dados')

        ref = db.reference('/')
        query_result = ref.order_by_child('numero').equal_to(numero).get()

        if query_result:
            for key in query_result:
                ref.child(key).update({
                    "gp2": dados_atualizados['gp2'],
                    "gp3": dados_atualizados['gp3'],
                    "idTelegram": dados_atualizados['idTelegram']
                })
                return jsonify({"success": True, "message": "Campos atualizados com sucesso"}), 200
        else:
            return jsonify({"error": "Número não encontrado"}), 404

    except ValueError:
        return jsonify({"error": "Número fornecido inválido"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def hello_world():
    return 'Hello, World!'
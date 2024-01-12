import os
import requests
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv
from telegram import Bot

# Configuração de logging
import logging
logging.basicConfig(level=logging.INFO)

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração dos bots
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot_token = os.getenv('bot_token')
bot1 = Bot(token=BOT_TOKEN)  # Instância do bot1 para criação de links de convite
bot2 = Bot(token=bot_token)  # Instância do bot2 para o chatbot do webhook

# Inicializa o aplicativo Flask
app = Flask(__name__)

# Configuração do Firebase
cred_obj = credentials.Certificate({
    "type": os.getenv('type'),
    "project_id": os.getenv('project_id'),
    "private_key_id": os.getenv('private_key_id'),
    "private_key": os.getenv('private_key').replace('\\n', '\n'),
    "client_email": os.getenv('client_email'),
    "client_id": os.getenv('client_id'),
    "auth_uri": os.getenv('auth_uri'),
    "token_uri": os.getenv('token_uri'),
    "auth_provider_x509_cert_url": os.getenv('auth_provider_x509_cert_url'),
    "client_x509_cert_url": os.getenv('client_x509_cert_url')
})
firebase_admin.initialize_app(cred_obj, {'databaseURL': os.getenv('firebase_url')})

# Função para criar links de convite no Telegram
def create_invite_link(chat_id):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/createChatInviteLink'
    payload = {'chat_id': chat_id}
    response = requests.post(url, json=payload)
    return response.json().get('result', {}).get('invite_link')

# Função para processar interações com o Firebase
def process_firebase_interaction(numero, telegram_user_id):
    ref = db.reference('/')
    query_result = ref.order_by_child('numero').equal_to(numero).get()

    if query_result:
        unique_key = next(iter(query_result))

        # Atualiza o idTelegram na Firebase
        ref.child(unique_key).update({"idTelegram": telegram_user_id})

        # Cria os links de convite para gp2 e gp3
        gp2_link = create_invite_link('-1002087905925')
        gp3_link = create_invite_link('-1001699690132')

        # Atualiza os links de convite na Firebase
        ref.child(unique_key).update({'gp2': gp2_link, 'gp3': gp3_link})
        return {"gp2_link": gp2_link, "gp3_link": gp3_link}
    else:
        return None

@app.route('/webhook/', methods=['POST'])
def handle_webhook():
    update = request.json
    logging.info("Webhook recebido: %s", update)

    if update.get("message") and update["message"].get("chat", {}).get("type") == "private":
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        telegram_user_id = update["message"].get("from", {}).get("id")

        if text == "/start":
            bot2.send_message(chat_id=chat_id, text="Digite seu telefone com 55+DDD+numero, sem os sinais de adição (+).")
            return jsonify({"status": "ok"})

        elif text.isdigit() and len(text) >= 10:
            result = process_firebase_interaction(int(text), telegram_user_id)

            if result:
                bot2.send_message(chat_id=chat_id, text=f"Seus links de convite foram atualizados.\nGP2: {result['gp2_link']}\nGP3: {result['gp3_link']}")
            else:
                bot2.send_message(chat_id=chat_id, text="Número não encontrado. Tente novamente.")

            return jsonify({"status": "ok"})

    return jsonify({"status": "ok"})

@app.route('/read/<numero>', methods=['GET'])
def read_record(numero):
    try:
        numero = int(numero)
    except ValueError:
        return jsonify({"error": "Número fornecido inválido"}), 400

    logging.info("Consultando número: %s", numero)
    ref = db.reference('/')
    query = ref.order_by_child('numero').equal_to(numero).get()

    if query:
        logging.info("Resultado da consulta: %s", query)
        return jsonify(query), 200
    else:
        return jsonify({"error": "Nenhum registro encontrado para o número fornecido"}), 404

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=os.getenv('PORT', 8181))
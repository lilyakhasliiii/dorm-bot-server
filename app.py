from flask import Flask, request, jsonify
from flask_cors import CORS
from telegram_init_data import validate, parse
import requests
import os

app = Flask(__name__)
CORS(app, resources={r"/send": {"origins": "*"}})

BOT_TOKEN = os.environ.get("BOT_TOKEN", "ВАШ_ТОКЕН")
CHAT_ID = os.environ.get("CHAT_ID", "ID_ГРУППЫ")

@app.route('/send', methods=['POST'])
def send_complaint():
    data = request.json
    init_data = data.get('initData', '')

    try:
        validate(init_data, BOT_TOKEN)
        parsed = parse(init_data)
        user = parsed.get('user', {})
    except Exception as e:
        return jsonify({"ok": False, "error": "Ошибка проверки"}), 401

    category = data.get('category')
    building = data.get('building', '')
    room = data.get('room', '')
    description = data.get('description', '').strip()

    username = f"@{user['username']}" if user.get('username') else f"{user.get('first_name','')} (ID: {user.get('id')})"
    names = {'noise': 'Жалоба на шум', 'neighbors': 'Жалоба на соседей', 'other': 'Другое'}

    text = f"🚨 НОВАЯ ЖАЛОБА\n👤 {username}\n📂 {names.get(category, category)}\n"
    if building: text += f"🏢 {building}\n"
    if room: text += f"🚪 Комната: {room}\n"
    text += f"📝 {description}"

    resp = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text}
    )
    if resp.status_code == 200:
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "Ошибка отправки в Telegram"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

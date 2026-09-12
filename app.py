import os
import json
from flask import Flask, render_template, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

if not firebase_admin._apps:
    cred_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')
    if cred_json:
        cred_dict = json.loads(cred_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)

db = firestore.client() if firebase_admin._apps else None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users')
@app.route('/api/users')
def get_users():
    if not db:
        return jsonify({'error': 'Database not initialized'}), 500
    try:
        users_ref = db.collection('users')
        docs = users_ref.stream()
        users_list = [{**doc.to_dict(), 'id': doc.id} for doc in docs]
        return jsonify(users_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
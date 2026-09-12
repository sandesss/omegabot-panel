import os
import json
from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Initialize Firebase via Render Environment Variable o Local JSON file
cred_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')
if cred_json:
    cred_dict = json.loads(cred_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
else:
    try:
        cred = credentials.Certificate("FIREBASE_CREDENTIALS_JSON.json")
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception:
        db = None

@app.route('/')
def index():
    users = []
    if db:
        docs = db.collection('users').stream()
        for doc in docs:
            data = doc.to_dict()
            data['hwid'] = doc.id
            users.append(data)
    return render_template('index.html', users=users)

@app.route('/api/register', methods=['POST'])
def register_user():
    if not db:
        return jsonify({'error': 'Database not initialized'}), 500
    data = request.json
    hwid = data.get('hwid')
    ip = data.get('ip')
    status = data.get('status', 'locked')
    action = data.get('action', 'none')
    
    if not hwid:
        return jsonify({'error': 'HWID required'}), 400
        
    doc_ref = db.collection('users').document(hwid)
    doc_ref.set({
        'ip': ip,
        'status': status,
        'action': action,
        'last_seen': firestore.SERVER_TIMESTAMP
    }, merge=True)
    
    return jsonify({'success': True})

@app.route('/api/users', methods=['GET'])
def get_users():
    if not db:
        return jsonify([])
    users = []
    docs = db.collection('users').stream()
    for doc in docs:
        d = doc.to_dict()
        d['hwid'] = doc.id
        users.append(d)
    return jsonify(users)

@app.route('/api/unlock/<hwid>', methods=['POST'])
def unlock_user(hwid):
    if not db:
        return jsonify({'error': 'Database not initialized'}), 500
    try:
        db.collection('users').document(hwid).set({'status': 'unlocked'}, merge=True)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fix/<hwid>', methods=['POST'])
def fix_user(hwid):
    if not db:
        return jsonify({'error': 'Database not initialized'}), 500
    try:
        db.collection('users').document(hwid).set({'status': 'unlocked'}, merge=True)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clear/<hwid>', methods=['POST'])
def clear_user(hwid):
    if not db:
        return jsonify({'error': 'Database not initialized'}), 500
    try:
        db.collection('users').document(hwid).set({'action': 'clear'}, merge=True)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
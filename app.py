import os
from flask import Flask, render_template, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Siguraduhing na-initialize ang Firebase gamit ang credentials file o environment variable
if not firebase_admin._apps:
    cred = credentials.Certificate("FIREBASE_CREDENTIALS_JSON.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route('/')
def index():
    try:
        # Kunin ang mga clients mula sa Firestore database
        users_ref = db.collection('clients') # Palitan ang 'clients' kung iba ang pangalan ng collection mo
        docs = users_ref.stream()
        users = []
        for doc in docs:
            data = doc.to_dict()
            data['hwid'] = doc.id
            users.append(data)
    except Exception as e:
        print(f"Error sa pagkuha ng database: {e}")
        users = []
        
    return render_template('index.html', users=users)

@app.route('/api/clear/<hwid>', methods=['POST'])
def api_clear(hwid):
    try:
        db.collection('clients').document(hwid).update({
            'action': 'clear'
        })
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@app.route('/api/stop_internet/<hwid>', methods=['POST'])
def api_stop_internet(hwid):
    try:
        db.collection('clients').document(hwid).update({
            'action': 'stop_internet'
        })
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@app.route('/api/restore_internet/<hwid>', methods=['POST'])
def api_restore_internet(hwid):
    try:
        db.collection('clients').document(hwid).update({
            'action': 'restore_internet'
        })
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@app.route('/api/fix/<hwid>', methods=['POST'])
def api_fix(hwid):
    try:
        db.collection('clients').document(hwid).update({
            'action': 'fix',
            'status': 'unlocked'
        })
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
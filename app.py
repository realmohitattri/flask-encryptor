from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from cryptography.fernet import Fernet
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'vault'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

key_file = os.path.join(UPLOAD_FOLDER, 'key.key')
if not os.path.exists(key_file):
    with open(key_file, 'wb') as f:
        f.write(Fernet.generate_key())

with open(key_file, 'rb') as f:
    key = f.read()
fernet = Fernet(key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt_file():
    file = request.files['file']
    if not file:
        flash("No file selected!")
        return redirect(url_for('index'))

    filename = file.filename
    data = file.read()
    encrypted = fernet.encrypt(data)

    with open(os.path.join(UPLOAD_FOLDER, filename + '.vault'), 'wb') as f:
        f.write(encrypted)

    flash(f"File '{filename}' encrypted and saved!")
    return redirect(url_for('index'))

@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt():
    if request.method == 'POST':
        filename = request.form['filename']
        try:
            with open(os.path.join(UPLOAD_FOLDER, filename), 'rb') as f:
                encrypted_data = f.read()
            decrypted_data = fernet.decrypt(encrypted_data)
            output_path = os.path.join(UPLOAD_FOLDER, 'decrypted_' + filename.replace('.vault', ''))
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            return send_file(output_path, as_attachment=True)
        except Exception:
            flash("Decryption failed! Check filename.")
            return redirect(url_for('decrypt'))
    return render_template('decrypt.html')

if __name__ == '__main__':
    app.run(debug=True)

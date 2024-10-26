from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import os
import random
import string

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["pastes_database"]
pastes_collection = db["pastes"]

def generate_random_project_name():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/paste', methods=['GET', 'POST'])
def paste():
    if request.method == 'POST':
        content = request.form['content']
        project_name = request.form.get('project_name').strip()

        if project_name == "custom":
            project_name = request.form.get('custom_project_name').strip()

        if not content:
            return "Konten tidak boleh kosong.", 400
        if not project_name:
            return "Nama proyek tidak boleh kosong.", 400

        # Check if project_name already exists in MongoDB
        if pastes_collection.find_one({"project_name": project_name}):
            return "Nama proyek sudah ada. Gunakan nama lain.", 400

        # Save paste to MongoDB
        try:
            pastes_collection.insert_one({"project_name": project_name, "content": content})
        except Exception as e:
            print(e)  # Optional: for debugging purposes
            return "Terjadi kesalahan saat menyimpan paste.", 500

        return redirect(url_for('view_paste', project_name=project_name))

    return render_template('paste.html')

@app.route('/paste/<project_name>')
def view_paste(project_name):
    paste = pastes_collection.find_one({"project_name": project_name})
    if not paste:
        return "Paste tidak ditemukan", 404

    return render_template('view_paste.html', paste=paste)

if __name__ == '__main__':
    app.run(debug=True)

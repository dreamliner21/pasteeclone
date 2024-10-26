from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
import random
import string

app = Flask(__name__)

# Konfigurasi folder untuk menyimpan file dan paste
UPLOAD_FOLDER = 'uploads'  # Folder untuk menyimpan file yang di-upload
PASTE_FOLDER = 'pastes'     # Folder untuk menyimpan paste
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Pastikan folder upload dan paste ada
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PASTE_FOLDER, exist_ok=True)

def generate_random_project_name():
    """Generate a random project name."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/paste', methods=['GET', 'POST'])
def paste():
    if request.method == 'POST':
        content = request.form['content']
        project_name = request.form.get('project_name').strip()  # Ambil dan hapus spasi

        # Ambil nilai dari input kustom jika "custom" dipilih
        if project_name == "custom":
            project_name = request.form.get('custom_project_name').strip()

        # Debug: Print nilai project_name dan content
        print(f"Project Name: '{project_name}', Content Length: {len(content)}")

        # Validasi input
        if not content:
            return "Konten tidak boleh kosong.", 400
        if not project_name:
            return "Nama proyek tidak boleh kosong. Gunakan nama lain atau pilih default.", 400

        # Cek apakah nama proyek sudah digunakan
        paste_file_path = os.path.join(PASTE_FOLDER, f"{project_name}.txt")
        print(f"Checking if project file exists at: {paste_file_path}")

        # Cek file
        if os.path.exists(paste_file_path):
            return "Nama proyek sudah ada. Gunakan nama lain.", 400
        else:
            print(f"File does not exist, proceeding to save.")

        # Simpan paste ke dalam file
        try:
            with open(paste_file_path, 'w') as paste_file:
                paste_file.write(content)
            print(f"Paste saved successfully as: {paste_file_path}")
        except Exception as e:
            print(f"Error saving paste: {e}")
            return "Terjadi kesalahan saat menyimpan paste.", 500

        return redirect(url_for('view_paste', project_name=project_name))

    return render_template('paste.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            download_url = url_for('uploaded_file', filename=filename, _external=True)
            return redirect(url_for('view_upload', download_url=download_url))

    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/view_upload')
def view_upload():
    download_url = request.args.get('download_url')
    return render_template('view_upload.html', download_url=download_url)

@app.route('/paste/<project_name>')
def view_paste(project_name):
    paste_file_path = os.path.join(PASTE_FOLDER, f"{project_name}.txt")
    if not os.path.exists(paste_file_path):
        return "Paste tidak ditemukan", 404

    with open(paste_file_path, 'r') as paste_file:
        content = paste_file.read()

    paste_url = url_for('view_paste', project_name=project_name, _external=True)
    download_url = url_for('download_paste', project_name=project_name, _external=True)
    return render_template('view_paste.html', paste={'content': content, 'project_name': project_name}, paste_url=paste_url, download_url=download_url)

@app.route('/download_paste/<project_name>')
def download_paste(project_name):
    paste_file_path = os.path.join(PASTE_FOLDER, f"{project_name}.txt")
    if not os.path.exists(paste_file_path):
        return "File tidak ditemukan", 404
    return send_from_directory(PASTE_FOLDER, f"{project_name}.txt", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

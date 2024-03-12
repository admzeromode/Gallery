import json
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory

app = Flask(__name__)

DATABASE = 'database.db'

# Create database if not exists
def create_database():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS images
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT)''')
    conn.commit()
    conn.close()

create_database()

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT id, filename FROM images")
    filenames = [{'id': row[0], 'filename': row[1]} for row in c.fetchall()]
    conn.close()
    return render_template('index.html', filenames=filenames)



@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
   

        file.save(filename)
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO images (filename) VALUES (?)", (file.filename,))
        conn.commit()
        conn.close()


        return json.dumps({'id_photo': file.filename})
    
    


@app.route('/delete', methods=['POST'])
def delete_image():
    id_photo = request.form.get('id_photo')
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM images WHERE filename = ?", (id_photo,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/update_image', methods=['POST'])
def update_image():
    filename = request.form.get('filename')
    new_file = request.files['new_image']
    
    if filename and new_file:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        new_filename = os.path.join(app.config['UPLOAD_FOLDER'], new_file.filename)
        new_file.save(new_filename)
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("UPDATE images SET filename = ? WHERE filename = ?", (new_file.filename, filename))
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))
    else:
        return "Ошибка при обновлении изображения"




if __name__ == '__main__':
    app.run(debug=True)


from flask import Flask, render_template, request, redirect, url_for, abort, send_file
from flask_wtf.csrf import CSRFProtect, CSRFError
import os
from werkzeug.utils import secure_filename
from marcFunctions import *
from zipfile import ZipFile

app = Flask(__name__)

# the secret key used to generate CSRF token
app.config['SECRET_KEY'] = 'testing_key_only'
...
# enable CSRF protection
app.config['DROPZONE_ENABLE_CSRF'] = True

csrf = CSRFProtect(app)

app.config['UPLOAD_EXTENSIONS'] = ['.pdf' ]
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = "uploads"

@app.errorhandler(400)
def custom400(error):
    # return error.description, 400
    return render_template('400.html', error = error)

@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413

@app.errorhandler(CSRFError)
def csrf_error(e):
    return e.description, 400

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download/', defaults={'session_id' : None, 'file_name' : None})
@app.route('/download/<session_id>/', defaults={'file_name' : None})
@app.route('/download/<session_id>/<file_name>')
def download(session_id, file_name):
    print(f"Downloading {session_id} - {file_name}")

    if session_id is None:
        abort(400, 'File not found on this server.')
    else:
        if file_name is None:
            try:
                download_file_path = os.path.join(app.config['UPLOAD_FOLDER'], session_id, f'{session_id}.zip')
                if(os.path.exists(download_file_path)):
                    print(f"Sending {download_file_path}")
                    return send_file(download_file_path ,as_attachment=True)
                else:
                    # print(f"{download_file_path} does not exist.")
                    abort(400, 'File not found on this server.')
            except Exception as e:
                abort(400, 'File not found on this server.')

        else:
            file_name = secure_filename(file_name)
            try:
                print(f"splitting {file_name}")
                file_name = os.path.splitext(file_name)[0] + ".mrc"
                # print(file_name)
                download_file_path = os.path.join(app.config['UPLOAD_FOLDER'], session_id, file_name)
                # print(download_file_path)
                if(os.path.exists(download_file_path)):
                    # print(f"Sending {download_file_path}")
                    return send_file(download_file_path ,as_attachment=True)
                else:
                    # print(f"{download_file_path} does not exist.")
                    abort(400, 'File not found on this server.')
            except Exception as e:
                abort(400, 'File not found on this server.')
@app.route('/', methods=['POST'])
def upload_file():
    my_files = request.files
    session_id = request.form['session_id']

    for item in my_files:
        uploaded_file = my_files.get(item)
        uploaded_file.filename = secure_filename(uploaded_file.filename)
        # print(f'Received {uploaded_file.filename}', flush=True)
        if uploaded_file.filename != '':
            file_ext = os.path.splitext(uploaded_file.filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            # print(f'{file_ext} is not a valid extension', flush=True)
            abort(400,f'{file_ext} is not a valid extension')
        saved_file_path = os.path.join(app.config['UPLOAD_FOLDER'], session_id, uploaded_file.filename)
        os.makedirs(os.path.dirname(saved_file_path), exist_ok=True)
        uploaded_file.save(saved_file_path)
        marc_file_path = pdf2marc(saved_file_path)
        # if (os.path.exists(marc_file_path)):
        #     return marc_file_path
        # else:
        #     abort(400,f'Could not process {uploaded_file.filename}')
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], session_id, f'{session_id}.zip')
    zipObj = ZipFile(zip_path, 'w')
    for file in os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], session_id)):
        if file.endswith('.mrc'):
            zipObj.write(os.path.join(app.config['UPLOAD_FOLDER'], session_id, file),file)
    zipObj.close()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="4000",debug=True)
    # app.run(host="0.0.0.0", port="4000")

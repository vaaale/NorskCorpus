from flask import Flask, request, redirect, url_for, send_from_directory
import json
import os

app = Flask(__name__)
UPLOAD_FOLDER="/tmp"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# @app.route("/")
# def index():
#     return json.dumps("Hello, World!")
#

def allowed_file(filename):
    return True


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        json_data = request.form.get("run_config")
        data = json.loads(json_data)
        if file and allowed_file(file.filename):
            print('**found file', file.filename)
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # for browser, add 'redirect' function on top of 'url_for'
            return url_for('uploaded_file', filename=filename)
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

if __name__ == '__main__':
    app.run()
from flask import Flask, jsonify, make_response, request, redirect, Response
from google import genai
from google.genai import types
from werkzeug.utils import secure_filename
from flask_cors import CORS
import json
import os

# If react makes OPTIONS request before the main one
# add 
# if request.method == 'OPTIONS':
# res = Response()
# res.headers['X-Content-Type-Options'] = '*'
# res.headers['Allow'] = ['GET', 'OPTIONS'] #or 'POST' instead of 'GET'
# return res


path = ''
app = Flask(__name__)
CORS(app)
# 20 mb max dataset size (max for gemini)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = os.path.dirname(os.path.abspath(__file__)) + '\\uploads\\'

response_template = {
                        "candidates": [{
                            "content": {
                            "parts": [{
                                "text": "Why tf do we need such a long template"
                            }]
                            }
                        }]
                    }

with open('config.json', 'r') as config_file:
    client = genai.Client(api_key=json.load(config_file)['API'])

chat = client.chats.create(model="gemini-2.0-flash", 
                        config=types.GenerateContentConfig(
                               system_instruction="You are a senior Data Scientist from Google. Your name is Datagment AI.",
                               temperature=1.0)
                            )


@app.route("/upload", methods=["POST"])
def load_dataset():
    """
    Upload a dataset to gemini
    """
    if 'file' not in request.files:
        print('No file attached in request')
        return redirect(request.url)
    file = request.files['file']

    if '.' not in file.filename:
        print('Format is unspecified. (.csv, .xlsx, .json, .sql, .xml)')
        return redirect(request.url)
    
    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)

    # Check format
    if path[path.find('.') + 1:] not in ['csv', 'xlsx', 'json', 'sql', 'xml']:
        return jsonify({'Error': 'Unsupported file format. Use .csv, .xlsx, .json, .sql, .xml formats'}), 500
    
    with open('./uploads/temp.txt', 'w', encoding='utf-8') as temp:
        temp.write(path)

    client.files.upload(file=path)
    
    global chat
    chat = client.chats.create(model="gemini-2.0-flash", 
                                config=types.GenerateContentConfig(
                               system_instruction="You are a senior Data Scientist from Google. Your name is Datagment AI.",
                               temperature=1.0), history=chat.get_history()
                            )
    chat.send_message('Uploaded ' + filename + ' in ' + path)

    # for f in client.files.list():
    #     print(' ', f.name)
    return jsonify({'Success': 'ok'}), 200


@app.route("/delete", methods=["POST"])
def delete_all():
    """
    Delete all datasets from gemini added earlier.
    """
    for f in client.files.list():
        client.files.delete(name=f.name)
    return jsonify({'Success': 'ok'}), 200



@app.route("/query/code", methods=['GET'])
def generate_code():
    """
    Ask to output code.
    """
    try:
        question = '''
        Only generate python code and nothing else. If you are using a dataset, read the dataset path from './uploads/temp.txt' file, open that file with encoding='utf-8'.  
        If the code output is an image, only save it in './uploads', do not show it. Handling errors related with files is unnecessary. 
        '''
        question += request.headers['question']
        response = chat.send_message(question)
        with open('executor.py', 'w') as executor:
            # Assuming gemini outputs '''python <code> '''
            executor.write(response.text[9:-4])
        return jsonify({'Success': 'ok'}), 200
    except Exception:
        return jsonify({'Error': 'Gemini failed to answer the query.'}), 500

@app.route('/query/execute', methods=['GET'])
def execute_generated_code():
    try:
        os.system("python executor.py")
        return jsonify({'Success': 'ok'}), 200
    except Exception:
        return jsonify({'Error': 'Couldnt execute code'}), 500

    

@app.route("/query/text", methods=["GET"])
def ask():
    """
    Ask for text response.
    """
    if request.method == 'OPTIONS':
        res = Response()
        res.headers['X-Content-Type-Options'] = '*'
        res.headers['Allow'] = ['GET', 'OPTIONS']
        return res
    
    try:
        question = request.headers['question']
        response = chat.send_message(question)
        print(response.text)
        
        if (request.headers['debug'] == 'True'):
            return response.text

        ans = response_template
        ans['candidates'][0]['content']['parts'][0]['text'] = response.text
        return jsonify(ans), 200
    except Exception:
        return jsonify({'Error': 'Gemini failed to answer the query.'}), 500

@app.route("/history", methods=["GET"])
def get_history():
    return jsonify(chat.get_history()), 200

if __name__ == "__main__":
    # Run on localhost
    app.run(host="0.0.0.0", port=5000, debug=True)
    # execute_generated_code()
    
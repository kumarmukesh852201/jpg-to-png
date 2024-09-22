from flask import Flask, render_template, request, send_file , abort
from PIL import Image
import io
import requests

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 15 * 1024 * 1024 # 15 MB limit

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        try:
            # Handle file upload
            if 'file' in request.files and request.files['file'].filename != '':
                file = request.files['file']
                if file:
                    img = Image.open(file)
                    return convert_image(img)
            # Handle URL upload
            elif 'url' in request.form and request.form['url'] != '':
                url = request.form['url']
                try:
                    response = requests.get(url)
                    response.raise_for_status()  # Check if the request was successful
                    img = Image.open(io.BytesIO(response.content))
                    return convert_image(img)
                except requests.exceptions.RequestException as e:
                    return f"Failed to fetch image from URL: {e}"
                except IOError:
                    return "The provided URL does not contain a valid image."
        except IOError:
            abort (413)
    return render_template('upload.html')

def convert_image(img):
    img = img.convert('RGB')
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='converted.png')

@app.errorhandler(413)
def request_entity_too_large(error):
    return "The uploaded file size exceeds the 15 MB limit. Please upload a smaller file.", 413

# if __name__ == '__main__':
#     app.run(debug=True)

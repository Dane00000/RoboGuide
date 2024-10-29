from flask import Flask, render_template_string, request, jsonify, redirect, url_for, send_from_directory
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'  # Folder to save uploaded videos
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'mov', 'avi', 'mkv'}  # Allowed video file extensions

# Predefined exhibit information
exhibit_info = {
    "Mona Lisa": "The Mona Lisa is a portrait painting by the Italian artist Leonardo da Vinci, created in the early 16th century. It is one of the most famous works of art in the world.",
    "The Starry Night": "The Starry Night is an oil on canvas painting by Vincent van Gogh, painted in June 1889. It depicts a swirling night sky over a quiet town.",
    "Tutankhamun's Mask": "Tutankhamun's funerary mask is a gold mask of the pharaoh Tutankhamun, made in the 14th century BC. It is one of the most famous artifacts from ancient Egypt.",
    "The Thinker": "The Thinker is a bronze sculpture by Auguste Rodin, representing a man in deep contemplation. It was created in the late 19th century.",
}

# Function to check if the uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# HTML Template with embedded CSS and JavaScript
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exhibit Information</title>
    <style>
        body {
            display: flex;
            height: 100vh;
            margin: 0;
            font-family: Arial, sans-serif;
        }
        #chat {
            width: 50%;
            padding: 20px;
            border-right: 1px solid #ccc;
            overflow-y: auto;
        }
        #video {
            width: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #f0f0f0;
        }
        #videoPlayer {
            width: 80%;
            max-width: 600px;
        }
    </style>
</head>
<body>

<div id="chat">
    <h2>Exhibit Information</h2>
    <div id="messages"></div>
    <input type="text" id="userInput" placeholder="Ask about a painting or exhibit..." />
    <button id="sendBtn">Send</button>
    <form id="uploadForm" enctype="multipart/form-data" method="POST" action="/upload">
        <input type="file" name="video" accept="video/*" required />
        <button type="submit">Upload Video</button>
    </form>
</div>

<div id="video">
    <video id="videoPlayer" controls>
        <source id="videoSource" src="" type="video/mp4">
        Your browser does not support the video tag.
    </video>
</div>

<script>
    const sendBtn = document.getElementById('sendBtn');
    const userInput = document.getElementById('userInput');
    const messages = document.getElementById('messages');
    const videoPlayer = document.getElementById('videoPlayer');
    const videoSource = document.getElementById('videoSource');

    sendBtn.addEventListener('click', async () => {
        const query = userInput.value.trim();
        if (!query) {
            messages.innerHTML += `<div>Please ask a valid question.</div>`;
            return;
        }

        messages.innerHTML += `<div>You: ${query}</div>`;
        userInput.value = '';

        const response = await fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ input: query })
        });
        const data = await response.json();
        messages.innerHTML += `<div>Information: ${data.response}</div>`;
    });

    function playVideo(videoPath) {
        videoSource.src = videoPath;
        videoPlayer.load();
        videoPlayer.play();
    }
</script>

</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json['input']

    # Check if the input matches any exhibit in our predefined dictionary
    for exhibit, info in exhibit_info.items():
        if exhibit.lower() in user_input.lower():
            return jsonify({'response': info})

    return jsonify({'response': "I don't have information on that exhibit."})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return redirect(request.url)

    file = request.files['video']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'response': "Invalid file type. Please upload a video file."})

    # Save the video file
    filename = file.filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Return the path to the uploaded video
    video_path = url_for('uploaded_file', filename=filename)
    return jsonify({'response': f'Video uploaded successfully! You can play it <a href="{video_path}">here</a>.'})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Create uploads folder if it doesn't exist
    app.run(debug=True)

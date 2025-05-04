from flask import Flask, jsonify, request, render_template, send_from_directory
import win32com.client
from flask_cors import CORS
import os
import pythoncom
import locale

app = Flask(__name__, static_folder='.')
CORS(app)  # Allow CORS for frontend communication

# Initialize COM for the application
pythoncom.CoInitialize()

# Voice categories mapping
VOICE_CATEGORIES = {
    "Microsoft David Desktop": {"accent": "US English", "gender": "Male"},
    "Microsoft Zira Desktop": {"accent": "US English", "gender": "Female"},
    "Microsoft Mark Desktop": {"accent": "British English", "gender": "Male"},
    "Microsoft Hazel Desktop": {"accent": "British English", "gender": "Female"},
    "Microsoft Pablo Desktop": {"accent": "Spanish", "gender": "Male"},
    "Microsoft Raul Desktop": {"accent": "Mexican Spanish", "gender": "Male"},
    "Microsoft Paul Desktop": {"accent": "British English", "gender": "Male"},
    "Microsoft Claude Desktop": {"accent": "French", "gender": "Male"},
    "Microsoft Julie Desktop": {"accent": "French", "gender": "Female"},
    "Microsoft Anna Desktop": {"accent": "US English", "gender": "Female"},
    "Microsoft Huihui Desktop": {"accent": "Chinese", "gender": "Female"},
    "Microsoft Stefan Desktop": {"accent": "German", "gender": "Male"},
    "Microsoft Hedda Desktop": {"accent": "German", "gender": "Female"},
    "Microsoft Haruka Desktop": {"accent": "Japanese", "gender": "Female"},
    "Microsoft Maria Desktop": {"accent": "Portuguese", "gender": "Female"}
}

# Serve the main page
@app.route("/")
def home():
    return send_from_directory(app.static_folder, 'page.html')

# Serve static files (CSS, JS, etc.)
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# API to handle text-to-speech
@app.route("/api/speak", methods=["POST"])
def speak_text():
    try:
        # Initialize COM for this thread
        pythoncom.CoInitialize()
        
        data = request.get_json()
        text = data.get("text", "")
        voice = data.get("voice", "default")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Initialize the text-to-speech engine
        speak = win32com.client.Dispatch("SAPI.SpVoice")
        
        # Set voice if specified
        if voice != "default":
            voices = speak.GetVoices()
            for v in voices:
                if v.GetDescription() == voice:
                    speak.Voice = v
                    break

        speak.Speak(text)
        
        # Uninitialize COM for this thread
        pythoncom.CoUninitialize()
        return jsonify({"message": "Text spoken successfully!"})

    except Exception as e:
        # Make sure to uninitialize COM even if there's an error
        try:
            pythoncom.CoUninitialize()
        except:
            pass
        return jsonify({"error": str(e)}), 500

# API to get available voices with categories
@app.route("/api/voices", methods=["GET"])
def get_voices():
    try:
        # Initialize COM for this thread
        pythoncom.CoInitialize()
        
        speak = win32com.client.Dispatch("SAPI.SpVoice")
        voices = speak.GetVoices()
        voice_list = []
        
        for voice in voices:
            voice_name = voice.GetDescription()
            voice_info = {
                "name": voice_name,
                "accent": VOICE_CATEGORIES.get(voice_name, {}).get("accent", "Unknown"),
                "gender": VOICE_CATEGORIES.get(voice_name, {}).get("gender", "Unknown")
            }
            voice_list.append(voice_info)
        
        # Sort voices by accent
        voice_list.sort(key=lambda x: (x["accent"], x["gender"]))
        
        # Uninitialize COM for this thread
        pythoncom.CoUninitialize()
        return jsonify({"voices": voice_list})
    except Exception as e:
        # Make sure to uninitialize COM even if there's an error
        try:
            pythoncom.CoUninitialize()
        except:
            pass
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Starting Text Reader application...")
    print("Please open http://localhost:8080 in your web browser")
    app.run(host="127.0.0.1", port=8080, debug=True)

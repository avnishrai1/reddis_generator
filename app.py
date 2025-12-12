from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import uuid
from datetime import datetime
from config import config
from services.llm_services import LLMService
from utils.validators import validate_input, sanitize_input
from groq import Groq

app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'development')])   
CORS(app)

# Initialize LLM service (choose provider)
llm_provider = 'groq'  # or 'anthropic'
api_key = app.config.get('GROQ_API_KEY') if llm_provider == 'groq' else app.config.get('ANTHROPIC_API_KEY')

if not api_key:
    raise ValueError(f"API key for {llm_provider} not found in environment variables")

llm_service = LLMService(api_key=api_key, provider=llm_provider)
self.client = Groq(api_key=api_key)

# In-memory session storage (use Redis in production)
sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        user_input = data.get('input', '').strip()
        
        # Validate input
        is_valid, message = validate_input(user_input)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Sanitize input
        user_input = sanitize_input(user_input)
        
        # Generate posts
        posts = llm_service.generate_posts(user_input)
        
        # Create session
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            'input': user_input,
            'posts': posts,
            'history': [],
            'created_at': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'session_id': session_id,
            'posts': posts
        })
    
    except Exception as e:
        print(f"Generate Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/regenerate', methods=['POST'])
def regenerate():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        feedback = data.get('feedback', '').strip()
        selected_post = data.get('selected_post')
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        # Validate feedback
        is_valid, message = validate_input(feedback, min_length=5)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        session_data = sessions[session_id]
        user_input = session_data['input']
        
        # Generate new posts with feedback
        posts = llm_service.generate_posts(user_input, feedback, selected_post)
        
        # Update session
        sessions[session_id]['posts'] = posts
        sessions[session_id]['history'].append({
            'feedback': feedback,
            'selected_post': selected_post,
            'posts': posts,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return jsonify({
            'session_id': session_id,
            'posts': posts
        })
    
    except Exception as e:
        print(f"Regenerate Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify(sessions[session_id])

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'provider': llm_provider})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
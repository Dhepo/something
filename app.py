from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
from werkzeug.utils import secure_filename
from midi_analyzer import MIDIAnalyzer
from recommendation_engine import RecommendationEngine
import traceback

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'mid', 'midi'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Get user preferences
            user_goals = request.form.getlist('goals')
            target_genre = request.form.get('target_genre', '')
            additional_notes = request.form.get('additional_notes', '')
            
            user_preferences = {
                'goals': user_goals,
                'target_genre': target_genre,
                'additional_notes': additional_notes
            }
            
            # Analyze the MIDI file
            analyzer = MIDIAnalyzer()
            analysis_result = analyzer.analyze_file(filepath)
            
            if analysis_result['success']:
                # Generate personalized recommendations
                rec_engine = RecommendationEngine()
                recommendations = rec_engine.generate_recommendations(
                    analysis_result['analysis'], 
                    user_preferences
                )
                
                result = {
                    'success': True,
                    'filename': filename,
                    'analysis': analysis_result['analysis'],
                    'recommendations': recommendations,
                    'user_preferences': user_preferences
                }
                
                # Clean up uploaded file
                os.remove(filepath)
                
                return jsonify(result)
            else:
                # Clean up uploaded file
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({'error': analysis_result['error']}), 400
        
        return jsonify({'error': 'Invalid file type. Please upload a MIDI file (.mid or .midi)'}), 400
    
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/results')
def results():
    return render_template('results.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

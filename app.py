from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import os
import json
from werkzeug.utils import secure_filename
from midi_analyzer import MIDIAnalyzer
from recommendation_engine import RecommendationEngine
from midi_generator import MIDIGenerator
import traceback
import tempfile
from io import BytesIO

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
            auto_improve = request.form.get('auto_improve') == 'on'
            
            user_preferences = {
                'goals': user_goals,
                'target_genre': target_genre,
                'additional_notes': additional_notes,
                'auto_improve': auto_improve,
                'improvement_duration': request.form.get('improvement_duration', 'extend_2x'),
                'custom_duration': request.form.get('custom_duration', '60'),
                'instruments': request.form.getlist('instruments')
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
                
                # Generate improved MIDI if requested
                if auto_improve and user_goals:
                    try:
                        generator = MIDIGenerator()
                        improved_midi_data = generator.apply_suggestions(
                            filepath, 
                            analysis_result['analysis'], 
                            recommendations, 
                            user_preferences
                        )
                        
                        if improved_midi_data:
                            # Save improved MIDI to session or temporary storage
                            import uuid
                            session_id = str(uuid.uuid4())
                            temp_improved_path = os.path.join(app.config['UPLOAD_FOLDER'], f'improved_{session_id}.mid')
                            
                            with open(temp_improved_path, 'wb') as f:
                                f.write(improved_midi_data)
                            
                            result['improved_midi'] = {
                                'available': True,
                                'download_id': session_id,
                                'filename': f'improved_{filename}'
                            }
                        else:
                            result['improved_midi'] = {
                                'available': False,
                                'error': 'Failed to generate improved MIDI'
                            }
                    except Exception as e:
                        print(f"Error generating improved MIDI: {e}")
                        result['improved_midi'] = {
                            'available': False,
                            'error': str(e)
                        }
                
                # Clean up original uploaded file
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

@app.route('/download/<download_id>')
def download_improved_midi(download_id):
    try:
        # Construct the improved MIDI file path
        improved_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'improved_{download_id}.mid')
        
        # Check if file exists
        if not os.path.exists(improved_file_path):
            return jsonify({'error': 'Improved MIDI file not found'}), 404
        
        # Send file for download
        return send_file(
            improved_file_path,
            as_attachment=True,
            download_name=f'improved_music_{download_id}.mid',
            mimetype='audio/midi'
        )
        
    except Exception as e:
        print(f"Error downloading improved MIDI: {e}")
        return jsonify({'error': 'Failed to download file'}), 500

@app.route('/cleanup/<download_id>', methods=['POST'])
def cleanup_improved_midi(download_id):
    try:
        # Clean up the temporary improved MIDI file
        improved_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'improved_{download_id}.mid')
        
        if os.path.exists(improved_file_path):
            os.remove(improved_file_path)
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'File not found'}), 404
            
    except Exception as e:
        print(f"Error cleaning up file: {e}")
        return jsonify({'error': 'Failed to cleanup file'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

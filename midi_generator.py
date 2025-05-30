import mido
from music21 import stream, note, chord, meter, tempo, pitch, duration, key
import numpy as np
import random
from music_theory import MusicTheoryHelper

class MIDIGenerator:
    def __init__(self):
        self.music_theory = MusicTheoryHelper()
        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    def apply_suggestions(self, original_filepath, analysis, recommendations, user_preferences):
        """Apply recommendations to generate an improved MIDI file"""
        try:
            # Load the original MIDI file
            original_midi = mido.MidiFile(original_filepath)
            
            # Parse with music21 for easier manipulation
            from music21 import converter
            score = converter.parse(original_filepath)
            
            # Apply improvements based on user goals and recommendations
            improved_score = self._apply_improvements(score, analysis, recommendations, user_preferences)
            
            # Export the improved score to MIDI
            return self._export_to_midi(improved_score)
            
        except Exception as e:
            print(f"Error applying suggestions: {e}")
            return None
    
    def _apply_improvements(self, score, analysis, recommendations, user_preferences):
        """Apply specific improvements based on analysis and recommendations"""
        user_goals = user_preferences.get('goals', [])
        target_genre = user_preferences.get('target_genre', '')
        
        improved_score = score.copy()
        
        # Apply harmony improvements
        if 'harmony' in user_goals:
            improved_score = self._improve_harmony(improved_score, analysis, target_genre)
        
        # Apply melody improvements
        if 'melody' in user_goals:
            improved_score = self._improve_melody(improved_score, analysis, target_genre)
        
        # Apply rhythm improvements
        if 'rhythm' in user_goals:
            improved_score = self._improve_rhythm(improved_score, analysis, target_genre)
        
        # Apply structure improvements
        if 'structure' in user_goals:
            improved_score = self._improve_structure(improved_score, analysis, target_genre)
        
        # Apply arrangement improvements
        if 'arrangement' in user_goals:
            improved_score = self._improve_arrangement(improved_score, analysis, target_genre)
        
        # Apply genre-specific improvements
        if 'genre' in user_goals and target_genre:
            improved_score = self._apply_genre_style(improved_score, analysis, target_genre)
        
        return improved_score
    
    def _improve_harmony(self, score, analysis, target_genre):
        """Improve harmonic progression"""
        try:
            key_info = analysis.get('key_signature', {})
            song_key = key_info.get('key', 'C major').split()[0] if key_info.get('key') else 'C'
            mode = key_info.get('mode', 'major')
            
            # Add bass line if missing
            bass_part = stream.Part()
            bass_part.id = 'Bass'
            
            # Generate simple bass line following chord progression
            chord_progression = self._generate_chord_progression(song_key, mode, target_genre)
            
            for i, chord_symbol in enumerate(chord_progression):
                measure_offset = i * 4  # 4 beats per measure
                bass_note = self._get_chord_root(chord_symbol, song_key)
                if bass_note:
                    n = note.Note(bass_note, quarterLength=4)
                    n.offset = measure_offset
                    bass_part.append(n)
            
            # Add the bass part to the score
            score.append(bass_part)
            
            return score
            
        except Exception as e:
            print(f"Error improving harmony: {e}")
            return score
    
    def _improve_melody(self, score, analysis, target_genre):
        """Improve melodic content"""
        try:
            melodic_info = analysis.get('melodic_analysis', {})
            key_info = analysis.get('key_signature', {})
            song_key = key_info.get('key', 'C major').split()[0] if key_info.get('key') else 'C'
            mode = key_info.get('mode', 'major')
            
            # Find the main melody part
            melody_part = None
            for part in score.parts:
                if len(part.flat.notes) > 0:
                    melody_part = part
                    break
            
            if melody_part:
                # Add harmonic intervals or countermelody
                harmony_part = stream.Part()
                harmony_part.id = 'Harmony'
                
                scale_notes = self.music_theory.get_scale_notes(song_key, mode)
                
                for n in melody_part.flat.notes:
                    if isinstance(n, note.Note):
                        # Add a harmony note (third or fifth above)
                        melody_pitch_class = n.pitch.pitchClass
                        harmony_interval = random.choice([2, 4])  # third or fifth
                        harmony_note_index = (scale_notes.index(self.note_names[melody_pitch_class]) + harmony_interval) % len(scale_notes)
                        harmony_pitch = scale_notes[harmony_note_index]
                        
                        harmony_note = note.Note(harmony_pitch, quarterLength=n.quarterLength)
                        harmony_note.offset = n.offset
                        harmony_part.append(harmony_note)
                
                score.append(harmony_part)
            
            return score
            
        except Exception as e:
            print(f"Error improving melody: {e}")
            return score
    
    def _improve_rhythm(self, score, analysis, target_genre):
        """Improve rhythmic elements"""
        try:
            # Add a simple drum/percussion track
            percussion_part = stream.Part()
            percussion_part.id = 'Percussion'
            
            # Create a basic rhythm pattern based on genre
            if target_genre == 'rock':
                pattern = self._create_rock_beat()
            elif target_genre == 'jazz':
                pattern = self._create_jazz_beat()
            elif target_genre == 'pop':
                pattern = self._create_pop_beat()
            else:
                pattern = self._create_basic_beat()
            
            # Repeat the pattern for the length of the song
            total_measures = analysis.get('structure_analysis', {}).get('total_measures', 8)
            for measure in range(total_measures):
                for beat_offset, drum_note in pattern:
                    n = note.Note('C4', quarterLength=0.25)  # Short percussion hit
                    n.offset = measure * 4 + beat_offset
                    percussion_part.append(n)
            
            score.append(percussion_part)
            
            return score
            
        except Exception as e:
            print(f"Error improving rhythm: {e}")
            return score
    
    def _improve_structure(self, score, analysis, target_genre):
        """Improve song structure"""
        try:
            # Add an intro and outro if missing
            structure_info = analysis.get('structure_analysis', {})
            total_measures = structure_info.get('total_measures', 0)
            
            if total_measures < 16:
                # Add a simple intro
                intro_part = stream.Part()
                intro_part.id = 'Intro'
                
                key_info = analysis.get('key_signature', {})
                song_key = key_info.get('key', 'C major').split()[0] if key_info.get('key') else 'C'
                
                # Simple arpeggio intro
                arpeggio_notes = [song_key + '3', song_key + '4', song_key + '5']
                for i, note_name in enumerate(arpeggio_notes):
                    n = note.Note(note_name, quarterLength=1)
                    n.offset = i
                    intro_part.append(n)
                
                # Insert at the beginning
                score.insert(0, intro_part)
            
            return score
            
        except Exception as e:
            print(f"Error improving structure: {e}")
            return score
    
    def _improve_arrangement(self, score, analysis, target_genre):
        """Improve overall arrangement"""
        try:
            basic_info = analysis.get('basic_info', {})
            tracks = basic_info.get('tracks', 1)
            
            if tracks == 1:
                # Add accompaniment chord track
                chord_part = stream.Part()
                chord_part.id = 'Chords'
                
                key_info = analysis.get('key_signature', {})
                song_key = key_info.get('key', 'C major').split()[0] if key_info.get('key') else 'C'
                mode = key_info.get('mode', 'major')
                
                chord_progression = self._generate_chord_progression(song_key, mode, target_genre)
                
                for i, chord_symbol in enumerate(chord_progression):
                    chord_notes = self._get_chord_notes(chord_symbol, song_key)
                    if chord_notes:
                        c = chord.Chord(chord_notes, quarterLength=4)
                        c.offset = i * 4
                        chord_part.append(c)
                
                score.append(chord_part)
            
            return score
            
        except Exception as e:
            print(f"Error improving arrangement: {e}")
            return score
    
    def _apply_genre_style(self, score, analysis, target_genre):
        """Apply genre-specific styling"""
        try:
            if target_genre == 'jazz':
                # Add swing feel (this is simplified)
                for part in score.parts:
                    for n in part.flat.notes:
                        if hasattr(n, 'quarterLength') and n.quarterLength == 0.5:
                            n.quarterLength = 0.67  # Swing eighth notes
            
            elif target_genre == 'rock':
                # Emphasize strong beats
                for part in score.parts:
                    for n in part.flat.notes:
                        if hasattr(n, 'offset') and n.offset % 1 == 0:  # On beat
                            if hasattr(n, 'volume'):
                                n.volume.velocity = min(127, n.volume.velocity + 20)
            
            return score
            
        except Exception as e:
            print(f"Error applying genre style: {e}")
            return score
    
    def _generate_chord_progression(self, key, mode, genre):
        """Generate a chord progression based on key, mode, and genre"""
        progressions = {
            'pop': ['I', 'V', 'vi', 'IV'],
            'rock': ['I', 'IV', 'V', 'I'],
            'jazz': ['ii', 'V', 'I', 'vi'],
            'folk': ['I', 'IV', 'I', 'V'],
            'default': ['I', 'vi', 'IV', 'V']
        }
        
        progression = progressions.get(genre, progressions['default'])
        chord_symbols = []
        
        scale_notes = self.music_theory.get_scale_notes(key, mode)
        if not scale_notes:
            return ['C', 'F', 'G', 'C']
        
        for roman in progression:
            if roman == 'I':
                chord_symbols.append(scale_notes[0])
            elif roman == 'ii':
                chord_symbols.append(scale_notes[1] + 'm')
            elif roman == 'IV':
                chord_symbols.append(scale_notes[3])
            elif roman == 'V':
                chord_symbols.append(scale_notes[4])
            elif roman == 'vi':
                chord_symbols.append(scale_notes[5] + 'm')
            else:
                chord_symbols.append(scale_notes[0])
        
        return chord_symbols
    
    def _get_chord_root(self, chord_symbol, key):
        """Get the root note of a chord"""
        # Simple implementation - just return the first character
        if chord_symbol:
            return chord_symbol[0] + '2'  # Bass octave
        return key + '2'
    
    def _get_chord_notes(self, chord_symbol, key):
        """Get the notes of a chord"""
        if not chord_symbol:
            return [key + '3', key + '4', key + '5']
        
        root = chord_symbol[0]
        if 'm' in chord_symbol:
            # Minor chord
            return [root + '3', root + '4', root + '5']
        else:
            # Major chord
            return [root + '3', root + '4', root + '5']
    
    def _create_basic_beat(self):
        """Create a basic 4/4 beat pattern"""
        return [(0, 'kick'), (1, 'snare'), (2, 'kick'), (3, 'snare')]
    
    def _create_rock_beat(self):
        """Create a rock beat pattern"""
        return [(0, 'kick'), (0.5, 'hihat'), (1, 'snare'), (1.5, 'hihat'), 
                (2, 'kick'), (2.5, 'hihat'), (3, 'snare'), (3.5, 'hihat')]
    
    def _create_jazz_beat(self):
        """Create a jazz beat pattern"""
        return [(0, 'kick'), (0.67, 'hihat'), (1.33, 'snare'), (2, 'kick'), 
                (2.67, 'hihat'), (3.33, 'snare')]
    
    def _create_pop_beat(self):
        """Create a pop beat pattern"""
        return [(0, 'kick'), (1, 'snare'), (2, 'kick'), (2.5, 'kick'), (3, 'snare')]
    
    def _export_to_midi(self, score):
        """Export the improved score to MIDI bytes"""
        try:
            # Create a temporary file path
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Write the score to MIDI
            score.write('midi', fp=temp_path)
            
            # Read the MIDI file as bytes
            with open(temp_path, 'rb') as f:
                midi_data = f.read()
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            return midi_data
            
        except Exception as e:
            print(f"Error exporting to MIDI: {e}")
            return None
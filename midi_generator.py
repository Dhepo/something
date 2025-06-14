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
            print(f"Starting MIDI improvement process...")
            
            # Load the original MIDI file with mido
            original_midi = mido.MidiFile(original_filepath)
            
            # Create improved version using mido directly for better compatibility
            improved_midi = self._create_improved_midi(original_midi, analysis, user_preferences)
            
            if improved_midi:
                # Convert to bytes
                import io
                midi_bytes = io.BytesIO()
                improved_midi.save(file=midi_bytes)
                midi_bytes.seek(0)
                return midi_bytes.read()
            
            return None
            
        except Exception as e:
            print(f"Error applying suggestions: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_improved_midi(self, original_midi, analysis, user_preferences):
        """Create improved MIDI using mido directly for better compatibility"""
        try:
            user_goals = user_preferences.get('goals', [])
            target_genre = user_preferences.get('target_genre', '')
            selected_instruments = user_preferences.get('instruments', [])
            duration_option = user_preferences.get('improvement_duration', 'extend_2x')
            
            print(f"Applying improvements for goals: {user_goals}")
            print(f"Selected instruments: {selected_instruments}")
            print(f"Duration option: {duration_option}")
            
            # Create new MIDI file - use type 1 to support multiple tracks
            improved_midi = mido.MidiFile(type=1, ticks_per_beat=original_midi.ticks_per_beat)
            
            # Copy original tracks and extend duration if needed
            duration_multiplier = self._get_duration_multiplier(duration_option, user_preferences)
            
            for track in original_midi.tracks:
                new_track = mido.MidiTrack()
                
                # Copy original track
                for msg in track:
                    new_track.append(msg.copy())
                
                # Extend track if needed
                if duration_multiplier > 1:
                    self._extend_track(new_track, original_midi, duration_multiplier)
                
                improved_midi.tracks.append(new_track)
            
            # Add improvements based on selected instruments
            if 'bass' in selected_instruments and ('harmony' in user_goals or 'arrangement' in user_goals):
                self._add_bass_track(improved_midi, analysis, target_genre)
            
            if 'drums' in selected_instruments and 'rhythm' in user_goals:
                self._add_drum_track(improved_midi, analysis, target_genre)
            
            if 'chords' in selected_instruments and ('harmony' in user_goals or 'arrangement' in user_goals):
                self._add_chord_track(improved_midi, analysis, target_genre)
                
            if 'strings' in selected_instruments:
                self._add_strings_track(improved_midi, analysis, target_genre)
                
            if 'lead' in selected_instruments and 'melody' in user_goals:
                self._add_lead_track(improved_midi, analysis, target_genre)
                
            if 'pad' in selected_instruments and 'arrangement' in user_goals:
                self._add_pad_track(improved_midi, analysis, target_genre)
            
            print(f"Successfully created improved MIDI with {len(improved_midi.tracks)} tracks")
            return improved_midi
            
        except Exception as e:
            print(f"Error creating improved MIDI: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _add_bass_track(self, midi_file, analysis, target_genre):
        """Add a simple bass track"""
        try:
            bass_track = mido.MidiTrack()
            bass_track.append(mido.Message('program_change', channel=1, program=32, time=0))  # Bass program
            
            # Simple bass pattern - play root notes on beats
            note = 36  # C2
            duration = 480  # Quarter note at 480 ticks per beat
            
            # Add some bass notes
            for i in range(8):  # 8 measures
                bass_track.append(mido.Message('note_on', channel=1, note=note, velocity=80, time=0 if i == 0 else duration * 4))
                bass_track.append(mido.Message('note_off', channel=1, note=note, velocity=0, time=duration))
                
                # Vary the bass note slightly
                if i % 4 == 3:
                    note += 5  # Go up a fourth
                elif i % 2 == 1:
                    note += 2  # Go up a whole step
                else:
                    note = 36  # Back to root
            
            midi_file.tracks.append(bass_track)
            print("Added bass track")
            
        except Exception as e:
            print(f"Error adding bass track: {e}")
    
    def _add_drum_track(self, midi_file, analysis, target_genre):
        """Add a simple drum track"""
        try:
            drum_track = mido.MidiTrack()
            
            # Create basic drum pattern
            kick = 36
            snare = 38
            hihat = 42
            
            # Simple 4/4 pattern
            pattern = [
                (kick, 0, 120),      # Kick on beat 1
                (hihat, 240, 80),    # Hi-hat on off-beat
                (snare, 240, 100),   # Snare on beat 2
                (hihat, 240, 80),    # Hi-hat
                (kick, 240, 120),    # Kick on beat 3
                (hihat, 240, 80),    # Hi-hat
                (snare, 240, 100),   # Snare on beat 4
                (hihat, 240, 80),    # Hi-hat
            ]
            
            # Repeat pattern for several measures
            for measure in range(4):
                for drum_note, time_offset, velocity in pattern:
                    drum_track.append(mido.Message('note_on', channel=9, note=drum_note, velocity=velocity, time=time_offset))
                    drum_track.append(mido.Message('note_off', channel=9, note=drum_note, velocity=0, time=120))
            
            midi_file.tracks.append(drum_track)
            print("Added drum track")
            
        except Exception as e:
            print(f"Error adding drum track: {e}")
    
    def _add_chord_track(self, midi_file, analysis, target_genre):
        """Add a simple chord accompaniment track"""
        try:
            chord_track = mido.MidiTrack()
            chord_track.append(mido.Message('program_change', channel=2, program=0, time=0))  # Piano
            
            # Simple chord progression
            chords = [
                [60, 64, 67],  # C major
                [65, 69, 72],  # F major  
                [67, 71, 74],  # G major
                [60, 64, 67],  # C major
            ]
            
            for i, chord in enumerate(chords):
                time_offset = 0 if i == 0 else 1920  # Whole note duration
                
                # Play chord
                for j, note in enumerate(chord):
                    chord_track.append(mido.Message('note_on', channel=2, note=note, velocity=60, time=time_offset if j == 0 else 0))
                
                # Release chord after whole note
                for note in chord:
                    chord_track.append(mido.Message('note_off', channel=2, note=note, velocity=0, time=1920 if note == chord[0] else 0))
            
            midi_file.tracks.append(chord_track)
            print("Added chord track")
            
        except Exception as e:
            print(f"Error adding chord track: {e}")
    
    def _apply_improvements(self, score, analysis, recommendations, user_preferences):
        """Apply specific improvements based on analysis and recommendations"""
        user_goals = user_preferences.get('goals', [])
        target_genre = user_preferences.get('target_genre', '')
        
        # Create a copy of the score for modifications
        improved_score = stream.Score()
        
        # Handle both scores with parts and flat streams
        if hasattr(score, 'parts') and score.parts:
            for part in score.parts:
                improved_score.append(part)
        else:
            # If it's a flat stream, convert it to a part
            part = stream.Part()
            for element in score.flatten():
                part.append(element)
            improved_score.append(part)
        
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
            if hasattr(score, 'parts') and score.parts:
                for part in score.parts:
                    if len(part.flatten().notes) > 0:
                        melody_part = part
                        break
            else:
                # Use the score itself as melody part if no parts
                melody_part = score
            
            if melody_part:
                # Add harmonic intervals or countermelody
                harmony_part = stream.Part()
                harmony_part.id = 'Harmony'
                
                scale_notes = self.music_theory.get_scale_notes(song_key, mode)
                
                for n in melody_part.flatten().notes:
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
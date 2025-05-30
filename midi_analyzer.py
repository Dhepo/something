import mido
from music21 import stream, note, chord, key, meter, tempo, pitch, interval
import numpy as np
from collections import defaultdict, Counter
import traceback

class MIDIAnalyzer:
    def __init__(self):
        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
    def analyze_file(self, filepath):
        """Analyze a MIDI file and extract musical information"""
        try:
            # Load MIDI file with mido for basic info
            midi_file = mido.MidiFile(filepath)
            
            # Load with music21 for advanced analysis
            try:
                from music21 import converter
                score = converter.parse(filepath)
            except Exception as e:
                print(f"Music21 parsing error: {e}")
                # Fallback to mido-only analysis
                return self._analyze_with_mido_only(midi_file)
            
            analysis = {
                'basic_info': self._get_basic_info(midi_file),
                'key_signature': self._analyze_key_signature(score),
                'tempo_info': self._analyze_tempo(score, midi_file),
                'notes_analysis': self._analyze_notes(score),
                'chord_progression': self._analyze_chords(score),
                'rhythm_patterns': self._analyze_rhythm(score),
                'structure_analysis': self._analyze_structure(score),
                'melodic_analysis': self._analyze_melody(score)
            }
            
            return {'success': True, 'analysis': analysis}
            
        except Exception as e:
            error_msg = f"Error analyzing MIDI file: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            return {'success': False, 'error': error_msg}
    
    def _analyze_with_mido_only(self, midi_file):
        """Fallback analysis using only mido"""
        try:
            notes = []
            tempo_changes = []
            current_tempo = 500000  # Default tempo (120 BPM)
            
            for track in midi_file.tracks:
                for msg in track:
                    if msg.type == 'note_on' and msg.velocity > 0:
                        notes.append({
                            'pitch': msg.note,
                            'velocity': msg.velocity,
                            'time': msg.time
                        })
                    elif msg.type == 'set_tempo':
                        current_tempo = msg.tempo
                        tempo_changes.append(msg.tempo)
            
            # Calculate BPM
            bpm = round(60000000 / current_tempo)
            
            # Basic note analysis
            pitches = [n['pitch'] for n in notes]
            note_counter = Counter([p % 12 for p in pitches])
            most_common_notes = [self.note_names[note] for note, _ in note_counter.most_common(5)]
            
            analysis = {
                'basic_info': {
                    'tracks': len(midi_file.tracks),
                    'total_notes': len(notes),
                    'duration_ticks': sum(track[-1].time for track in midi_file.tracks if track),
                    'ticks_per_beat': midi_file.ticks_per_beat
                },
                'tempo_info': {
                    'average_bpm': bpm,
                    'tempo_changes': len(tempo_changes)
                },
                'notes_analysis': {
                    'total_notes': len(notes),
                    'pitch_range': {'lowest': min(pitches), 'highest': max(pitches)} if pitches else {'lowest': 0, 'highest': 0},
                    'most_common_notes': most_common_notes,
                    'average_velocity': np.mean([n['velocity'] for n in notes]) if notes else 0
                },
                'key_signature': {'key': 'Unknown', 'confidence': 0},
                'chord_progression': {'chords': [], 'progression_type': 'Unknown'},
                'rhythm_patterns': {'time_signature': '4/4', 'rhythmic_complexity': 'Simple'},
                'structure_analysis': {'sections': [], 'repetitions': 0},
                'melodic_analysis': {'contour': 'Unknown', 'intervals': []}
            }
            
            return {'success': True, 'analysis': analysis}
            
        except Exception as e:
            return {'success': False, 'error': f"Fallback analysis failed: {str(e)}"}
    
    def _get_basic_info(self, midi_file):
        """Extract basic MIDI file information"""
        return {
            'format': midi_file.type,
            'tracks': len(midi_file.tracks),
            'ticks_per_beat': midi_file.ticks_per_beat,
            'length_seconds': midi_file.length
        }
    
    def _analyze_key_signature(self, score):
        """Analyze the key signature of the piece"""
        try:
            key_sig = score.analyze('key')
            return {
                'key': str(key_sig),
                'mode': key_sig.mode,
                'confidence': 0.8  # music21's key analysis is generally reliable
            }
        except:
            return {'key': 'C major', 'mode': 'major', 'confidence': 0.3}
    
    def _analyze_tempo(self, score, midi_file):
        """Analyze tempo information"""
        try:
            tempo_marks = score.getElementsByClass(tempo.TempoIndication)
            if tempo_marks:
                avg_bpm = np.mean([t.getQuarterBPM() for t in tempo_marks if t.getQuarterBPM()])
            else:
                # Estimate from MIDI file length and note density
                avg_bpm = 120  # Default
            
            return {
                'average_bpm': round(avg_bpm),
                'tempo_changes': len(tempo_marks),
                'tempo_stability': 'Stable' if len(tempo_marks) <= 1 else 'Variable'
            }
        except:
            return {'average_bpm': 120, 'tempo_changes': 0, 'tempo_stability': 'Unknown'}
    
    def _analyze_notes(self, score):
        """Analyze note patterns and characteristics"""
        try:
            notes = score.flatten().notes
            pitches = []
            velocities = []
            
            for n in notes:
                if isinstance(n, note.Note):
                    pitches.append(n.pitch.midi)
                    velocities.append(getattr(n, 'velocity', 64))
                elif isinstance(n, chord.Chord):
                    pitches.extend([p.midi for p in n.pitches])
                    velocities.extend([getattr(n, 'velocity', 64)] * len(n.pitches))
            
            if not pitches:
                return {'total_notes': 0, 'pitch_range': {'lowest': 0, 'highest': 0}, 
                       'most_common_notes': [], 'average_velocity': 0}
            
            # Note name analysis
            note_counter = Counter([self.note_names[p % 12] for p in pitches])
            most_common_notes = [note for note, _ in note_counter.most_common(5)]
            
            return {
                'total_notes': len(pitches),
                'pitch_range': {
                    'lowest': min(pitches),
                    'highest': max(pitches)
                },
                'most_common_notes': most_common_notes,
                'average_velocity': round(np.mean(velocities))
            }
        except Exception as e:
            print(f"Note analysis error: {e}")
            return {'total_notes': 0, 'pitch_range': {'lowest': 0, 'highest': 0}, 
                   'most_common_notes': [], 'average_velocity': 0}
    
    def _analyze_chords(self, score):
        """Analyze chord progressions"""
        try:
            chords_found = []
            
            # Extract chords from the score
            for element in score.flatten():
                if isinstance(element, chord.Chord):
                    chord_symbol = element.commonName or element.pitchedCommonName
                    chords_found.append(chord_symbol)
            
            # If no explicit chords, try to identify them from note combinations
            if not chords_found:
                # Group notes by time to find potential chords
                notes_by_time = defaultdict(list)
                for n in score.flatten().notes:
                    if isinstance(n, note.Note):
                        notes_by_time[float(n.offset)].append(n)
                
                for time_point, notes_at_time in notes_by_time.items():
                    if len(notes_at_time) >= 3:  # Potential chord
                        pitches = [n.pitch for n in notes_at_time]
                        try:
                            chord_obj = chord.Chord(pitches)
                            chords_found.append(chord_obj.commonName)
                        except:
                            pass
            
            # Analyze progression type
            progression_type = self._classify_progression(chords_found)
            
            return {
                'chords': chords_found[:10],  # Limit to first 10 chords
                'progression_type': progression_type,
                'total_chords': len(chords_found)
            }
        except Exception as e:
            print(f"Chord analysis error: {e}")
            return {'chords': [], 'progression_type': 'Unknown', 'total_chords': 0}
    
    def _classify_progression(self, chords):
        """Classify the type of chord progression"""
        if not chords:
            return 'Unknown'
        
        chord_types = [chord.split() for chord in chords if chord]
        
        # Simple classification based on common patterns
        if any('major' in str(chord).lower() for chord in chords):
            if any('minor' in str(chord).lower() for chord in chords):
                return 'Mixed Major/Minor'
            return 'Predominantly Major'
        elif any('minor' in str(chord).lower() for chord in chords):
            return 'Predominantly Minor'
        else:
            return 'Varied'
    
    def _analyze_rhythm(self, score):
        """Analyze rhythmic patterns"""
        try:
            time_sigs = score.getElementsByClass('TimeSignature')
            if time_sigs:
                time_sig = str(time_sigs[0])
            else:
                time_sig = '4/4'  # Default
            
            # Analyze note durations for rhythmic complexity
            durations = []
            for n in score.flatten().notes:
                durations.append(float(n.duration.quarterLength))
            
            if durations:
                unique_durations = len(set(durations))
                if unique_durations <= 3:
                    complexity = 'Simple'
                elif unique_durations <= 6:
                    complexity = 'Moderate'
                else:
                    complexity = 'Complex'
            else:
                complexity = 'Unknown'
            
            return {
                'time_signature': time_sig,
                'rhythmic_complexity': complexity,
                'unique_durations': len(set(durations)) if durations else 0
            }
        except Exception as e:
            print(f"Rhythm analysis error: {e}")
            return {'time_signature': '4/4', 'rhythmic_complexity': 'Unknown', 'unique_durations': 0}
    
    def _analyze_structure(self, score):
        """Analyze musical structure and form"""
        try:
            # Simple structure analysis based on repetitions and sections
            measures = score.getElementsByClass('Measure')
            total_measures = len(measures)
            
            # Look for repeated sections (simplified)
            sections = []
            if total_measures > 0:
                if total_measures <= 16:
                    sections.append({'name': 'Short Form', 'measures': f'1-{total_measures}'})
                elif total_measures <= 32:
                    sections.append({'name': 'Verse', 'measures': '1-16'})
                    sections.append({'name': 'Chorus', 'measures': '17-32'})
                else:
                    sections.append({'name': 'Intro', 'measures': '1-8'})
                    sections.append({'name': 'Verse', 'measures': '9-24'})
                    sections.append({'name': 'Chorus', 'measures': '25-40'})
                    if total_measures > 40:
                        sections.append({'name': 'Additional Sections', 'measures': f'41-{total_measures}'})
            
            return {
                'total_measures': total_measures,
                'sections': sections,
                'estimated_form': 'AABA' if total_measures > 24 else 'AB'
            }
        except Exception as e:
            print(f"Structure analysis error: {e}")
            return {'total_measures': 0, 'sections': [], 'estimated_form': 'Unknown'}
    
    def _analyze_melody(self, score):
        """Analyze melodic characteristics"""
        try:
            melody_notes = []
            
            # Extract melody (highest notes or first track)
            for n in score.flatten().notes:
                if isinstance(n, note.Note):
                    melody_notes.append(n.pitch.midi)
                elif isinstance(n, chord.Chord):
                    # Take highest note of chord as melody
                    melody_notes.append(max(p.midi for p in n.pitches))
            
            if len(melody_notes) < 2:
                return {'contour': 'Insufficient data', 'intervals': [], 'range': 0}
            
            # Analyze melodic contour
            intervals = []
            for i in range(1, len(melody_notes)):
                interval = melody_notes[i] - melody_notes[i-1]
                intervals.append(interval)
            
            # Classify contour
            if not intervals:
                contour = 'Static'
            else:
                avg_interval = np.mean(intervals)
                if abs(avg_interval) < 1:
                    contour = 'Static'
                elif avg_interval > 2:
                    contour = 'Ascending'
                elif avg_interval < -2:
                    contour = 'Descending'
                else:
                    contour = 'Undulating'
            
            melodic_range = max(melody_notes) - min(melody_notes) if melody_notes else 0
            
            return {
                'contour': contour,
                'intervals': intervals[:10],  # First 10 intervals
                'range': melodic_range,
                'average_interval': round(np.mean(intervals), 2) if intervals else 0
            }
        except Exception as e:
            print(f"Melody analysis error: {e}")
            return {'contour': 'Unknown', 'intervals': [], 'range': 0, 'average_interval': 0}

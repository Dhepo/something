"""
Music theory utilities for analysis and recommendations
"""

class MusicTheoryHelper:
    def __init__(self):
        self.note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.major_scale_intervals = [0, 2, 4, 5, 7, 9, 11]
        self.minor_scale_intervals = [0, 2, 3, 5, 7, 8, 10]
        
        # Common chord progressions in major keys (using Roman numerals as indices)
        self.common_progressions = {
            'pop': [[0, 5, 3, 4], [0, 4, 0, 5]],  # I-vi-IV-V, I-V-I-vi
            'jazz': [[0, 3, 4, 5], [1, 4, 0]],    # I-vi-ii-V, ii-V-I
            'folk': [[0, 4, 0, 5], [0, 0, 4, 5]],  # I-V-I-vi, I-I-V-vi
            'rock': [[0, 2, 4, 0], [0, 4, 5, 0]]   # I-iii-V-I, I-V-vi-I
        }
        
        # Scale degrees for chord suggestions
        self.major_chords = {
            0: 'major',   # I
            1: 'minor',   # ii
            2: 'minor',   # iii
            3: 'major',   # IV
            4: 'major',   # V
            5: 'minor',   # vi
            6: 'diminished'  # vii°
        }
        
        self.minor_chords = {
            0: 'minor',   # i
            1: 'diminished',  # ii°
            2: 'major',   # III
            3: 'minor',   # iv
            4: 'minor',   # v
            5: 'major',   # VI
            6: 'major'    # VII
        }
    
    def get_scale_notes(self, root_note, mode='major'):
        """Get notes in a scale given the root note and mode"""
        if root_note not in self.note_names:
            return []
        
        root_index = self.note_names.index(root_note)
        intervals = self.major_scale_intervals if mode == 'major' else self.minor_scale_intervals
        
        scale_notes = []
        for interval in intervals:
            note_index = (root_index + interval) % 12
            scale_notes.append(self.note_names[note_index])
        
        return scale_notes
    
    def get_chord_from_scale_degree(self, root_note, scale_degree, mode='major'):
        """Get chord based on scale degree (0-6)"""
        scale_notes = self.get_scale_notes(root_note, mode)
        if not scale_notes or scale_degree >= len(scale_notes):
            return None
        
        chord_root = scale_notes[scale_degree]
        chord_type = self.major_chords[scale_degree] if mode == 'major' else self.minor_chords[scale_degree]
        
        return f"{chord_root} {chord_type}"
    
    def suggest_next_chords(self, current_chord, key, mode='major'):
        """Suggest next chords based on music theory"""
        suggestions = []
        
        # Get scale notes
        scale_notes = self.get_scale_notes(key, mode)
        if not scale_notes:
            return suggestions
        
        # Common progressions from each scale degree
        common_movements = {
            0: [3, 4, 5],  # I -> IV, V, vi
            1: [4, 0],     # ii -> V, I
            2: [5, 3],     # iii -> vi, IV
            3: [0, 1, 4],  # IV -> I, ii, V
            4: [0, 5],     # V -> I, vi
            5: [3, 4, 0],  # vi -> IV, V, I
            6: [0, 4]      # vii -> I, V
        }
        
        for degree, movements in common_movements.items():
            for next_degree in movements:
                chord = self.get_chord_from_scale_degree(key, next_degree, mode)
                if chord:
                    suggestions.append({
                        'chord': chord,
                        'function': self.get_chord_function(next_degree, mode),
                        'strength': self.get_progression_strength(degree, next_degree)
                    })
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def get_chord_function(self, scale_degree, mode='major'):
        """Get the harmonic function of a chord"""
        if mode == 'major':
            functions = {
                0: 'Tonic',
                1: 'Subdominant',
                2: 'Tonic',
                3: 'Subdominant',
                4: 'Dominant',
                5: 'Tonic',
                6: 'Dominant'
            }
        else:
            functions = {
                0: 'Tonic',
                1: 'Subdominant',
                2: 'Dominant/Tonic',
                3: 'Subdominant',
                4: 'Dominant',
                5: 'Subdominant',
                6: 'Subtonic'
            }
        
        return functions.get(scale_degree, 'Unknown')
    
    def get_progression_strength(self, from_degree, to_degree):
        """Rate the strength of a chord progression"""
        # Strong progressions
        strong_progressions = [
            (4, 0),  # V-I (dominant to tonic)
            (3, 0),  # IV-I (subdominant to tonic)
            (1, 4),  # ii-V
            (5, 3)   # vi-IV
        ]
        
        # Moderate progressions
        moderate_progressions = [
            (0, 3),  # I-IV
            (0, 5),  # I-vi
            (3, 4),  # IV-V
            (5, 4)   # vi-V
        ]
        
        progression = (from_degree, to_degree)
        
        if progression in strong_progressions:
            return 'Strong'
        elif progression in moderate_progressions:
            return 'Moderate'
        else:
            return 'Weak'
    
    def analyze_chord_progression_quality(self, chords, key, mode='major'):
        """Analyze the quality of a chord progression"""
        if not chords:
            return {'quality': 'Unknown', 'suggestions': []}
        
        scale_notes = self.get_scale_notes(key, mode)
        
        # Count functional movements
        strong_movements = 0
        total_movements = len(chords) - 1
        
        for i in range(len(chords) - 1):
            # Simplified analysis - this would need more sophisticated chord parsing
            strong_movements += 1 if 'major' in chords[i].lower() or 'minor' in chords[i].lower() else 0
        
        if total_movements == 0:
            quality = 'Single chord'
        elif strong_movements / total_movements > 0.7:
            quality = 'Strong'
        elif strong_movements / total_movements > 0.4:
            quality = 'Moderate'
        else:
            quality = 'Needs improvement'
        
        return {
            'quality': quality,
            'functional_strength': f"{strong_movements}/{total_movements}",
            'suggestions': self.suggest_progression_improvements(chords, key, mode)
        }
    
    def suggest_progression_improvements(self, chords, key, mode='major'):
        """Suggest improvements to a chord progression"""
        suggestions = []
        
        if len(chords) < 4:
            suggestions.append("Consider extending the progression to 4 or more chords for better flow")
        
        if not any(key in chord for chord in chords):
            suggestions.append(f"Consider starting or ending with the tonic chord ({key})")
        
        # Check for V-I resolution
        has_dominant_resolution = False
        scale_notes = self.get_scale_notes(key, mode)
        if len(scale_notes) >= 5:
            dominant_note = scale_notes[4]
            for i, chord in enumerate(chords[:-1]):
                if dominant_note in chord and key in chords[i + 1]:
                    has_dominant_resolution = True
                    break
        
        if not has_dominant_resolution:
            suggestions.append("Consider adding a dominant to tonic resolution for stronger harmonic movement")
        
        return suggestions
    
    def get_melody_suggestions(self, key, mode='major'):
        """Suggest melodic ideas based on key and mode"""
        scale_notes = self.get_scale_notes(key, mode)
        
        suggestions = []
        
        if scale_notes:
            suggestions.append({
                'type': 'Scale run',
                'description': f"Use ascending or descending {key} {mode} scale: {' - '.join(scale_notes)}"
            })
            
            suggestions.append({
                'type': 'Arpeggio',
                'description': f"Use chord tones: {scale_notes[0]} - {scale_notes[2]} - {scale_notes[4]}"
            })
            
            suggestions.append({
                'type': 'Pentatonic',
                'description': f"Use pentatonic notes: {scale_notes[0]} - {scale_notes[1]} - {scale_notes[2]} - {scale_notes[4]} - {scale_notes[5]}"
            })
            
            if mode == 'major':
                suggestions.append({
                    'type': 'Leading tone',
                    'description': f"Use the leading tone {scale_notes[6]} to resolve to {scale_notes[0]}"
                })
            
        return suggestions

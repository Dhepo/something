from music_theory import MusicTheoryHelper
import random

class RecommendationEngine:
    def __init__(self):
        self.music_theory = MusicTheoryHelper()
    
    def generate_recommendations(self, analysis, user_preferences=None):
        """Generate comprehensive recommendations based on analysis and user preferences"""
        if user_preferences is None:
            user_preferences = {'goals': [], 'target_genre': '', 'additional_notes': ''}
        
        user_goals = user_preferences.get('goals', [])
        target_genre = user_preferences.get('target_genre', '')
        
        # Generate all recommendations but prioritize based on user goals
        all_recommendations = {
            'harmonic_suggestions': self._get_harmonic_suggestions(analysis, target_genre),
            'melodic_suggestions': self._get_melodic_suggestions(analysis, target_genre),
            'rhythmic_suggestions': self._get_rhythmic_suggestions(analysis, target_genre),
            'structural_suggestions': self._get_structural_suggestions(analysis, target_genre),
            'arrangement_ideas': self._get_arrangement_ideas(analysis, target_genre),
            'development_strategies': self._get_development_strategies(analysis, target_genre),
            'genre_specific_tips': self._get_genre_specific_suggestions(analysis, target_genre),
            'personalized_priority': self._get_prioritized_suggestions(analysis, user_goals, target_genre)
        }
        
        # Add user context
        all_recommendations['user_context'] = {
            'goals': user_goals,
            'target_genre': target_genre,
            'notes': user_preferences.get('additional_notes', '')
        }
        
        return all_recommendations
    
    def _get_harmonic_suggestions(self, analysis):
        """Generate harmony-related suggestions"""
        suggestions = []
        
        key_info = analysis.get('key_signature', {})
        chord_info = analysis.get('chord_progression', {})
        
        key = key_info.get('key', 'C major').split()[0] if key_info.get('key') else 'C'
        mode = key_info.get('mode', 'major')
        
        # Chord progression suggestions
        if len(chord_info.get('chords', [])) < 4:
            suggestions.append({
                'category': 'Chord Progression',
                'title': 'Extend your chord progression',
                'description': 'Your piece has a short chord progression. Consider adding more chords for harmonic interest.',
                'specific_advice': self._suggest_chord_extensions(key, mode, chord_info.get('chords', []))
            })
        
        # Secondary dominants
        suggestions.append({
            'category': 'Advanced Harmony',
            'title': 'Add secondary dominants',
            'description': 'Secondary dominants can add sophisticated harmonic color.',
            'specific_advice': self._suggest_secondary_dominants(key, mode)
        })
        
        # Modal interchange
        if mode == 'major':
            suggestions.append({
                'category': 'Modal Color',
                'title': 'Try modal interchange',
                'description': 'Borrow chords from the parallel minor key for emotional depth.',
                'specific_advice': self._suggest_modal_interchange(key)
            })
        
        # Voice leading improvements
        suggestions.append({
            'category': 'Voice Leading',
            'title': 'Smooth voice leading',
            'description': 'Consider voice leading principles for smoother harmonic transitions.',
            'specific_advice': 'Move chord tones by the smallest intervals possible between changes.'
        })
        
        return suggestions
    
    def _get_melodic_suggestions(self, analysis):
        """Generate melody-related suggestions"""
        suggestions = []
        
        melodic_info = analysis.get('melodic_analysis', {})
        notes_info = analysis.get('notes_analysis', {})
        key_info = analysis.get('key_signature', {})
        
        key = key_info.get('key', 'C major').split()[0] if key_info.get('key') else 'C'
        mode = key_info.get('mode', 'major')
        
        contour = melodic_info.get('contour', 'Unknown')
        melodic_range = melodic_info.get('range', 0)
        
        # Range suggestions
        if melodic_range < 12:  # Less than an octave
            suggestions.append({
                'category': 'Melodic Range',
                'title': 'Expand melodic range',
                'description': f'Your melody spans {melodic_range} semitones. Consider expanding for more dramatic effect.',
                'specific_advice': f'Try extending melody up to {key} in the next octave or down to lower register.'
            })
        elif melodic_range > 24:  # More than two octaves
            suggestions.append({
                'category': 'Melodic Range',
                'title': 'Consider melodic focus',
                'description': f'Your melody has a wide range ({melodic_range} semitones). Consider focusing on a specific register.',
                'specific_advice': 'Create contrast by having sections focus on different octaves.'
            })
        
        # Contour suggestions
        if contour == 'Static':
            suggestions.append({
                'category': 'Melodic Movement',
                'title': 'Add melodic movement',
                'description': 'Your melody is quite static. Add more pitch variation for interest.',
                'specific_advice': 'Try incorporating steps and leaps to create melodic curves.'
            })
        elif contour == 'Ascending':
            suggestions.append({
                'category': 'Melodic Balance',
                'title': 'Balance ascending motion',
                'description': 'Your melody tends to ascend. Add descending passages for balance.',
                'specific_advice': 'Create melodic peaks followed by gentle descents.'
            })
        elif contour == 'Descending':
            suggestions.append({
                'category': 'Melodic Balance',
                'title': 'Balance descending motion',
                'description': 'Your melody tends to descend. Add ascending passages for lift.',
                'specific_advice': 'Build energy with ascending sequences and phrases.'
            })
        
        # Scale-based suggestions
        melody_suggestions = self.music_theory.get_melody_suggestions(key, mode)
        for suggestion in melody_suggestions[:2]:  # Limit to 2 suggestions
            suggestions.append({
                'category': 'Melodic Ideas',
                'title': suggestion['type'],
                'description': suggestion['description'],
                'specific_advice': f'This works well in {key} {mode} and can add melodic interest.'
            })
        
        return suggestions
    
    def _get_rhythmic_suggestions(self, analysis):
        """Generate rhythm-related suggestions"""
        suggestions = []
        
        rhythm_info = analysis.get('rhythm_patterns', {})
        tempo_info = analysis.get('tempo_info', {})
        
        complexity = rhythm_info.get('rhythmic_complexity', 'Unknown')
        bpm = tempo_info.get('average_bpm', 120)
        
        # Rhythmic complexity suggestions
        if complexity == 'Simple':
            suggestions.append({
                'category': 'Rhythmic Interest',
                'title': 'Add rhythmic variety',
                'description': 'Your rhythm is quite simple. Consider adding syncopation or varied note values.',
                'specific_advice': 'Try using dotted rhythms, triplets, or off-beat accents.'
            })
        elif complexity == 'Complex':
            suggestions.append({
                'category': 'Rhythmic Balance',
                'title': 'Balance complex rhythms',
                'description': 'Your rhythm is complex. Consider adding simpler sections for contrast.',
                'specific_advice': 'Use simple rhythms in verses and complex rhythms in choruses.'
            })
        
        # Tempo suggestions
        if bpm < 80:
            suggestions.append({
                'category': 'Energy and Pace',
                'title': 'Consider energy levels',
                'description': f'Your tempo ({bpm} BPM) is quite slow. This works for ballads but consider varying pace.',
                'specific_advice': 'Add a bridge or section with double-time feel to create contrast.'
            })
        elif bpm > 160:
            suggestions.append({
                'category': 'Energy and Pace',
                'title': 'Balance high energy',
                'description': f'Your tempo ({bpm} BPM) is quite fast. Consider adding slower sections for contrast.',
                'specific_advice': 'Use a half-time feel in verses or add a slower bridge section.'
            })
        
        # Groove suggestions
        suggestions.append({
            'category': 'Groove Development',
            'title': 'Develop rhythmic motifs',
            'description': 'Create rhythmic patterns that repeat and develop throughout the song.',
            'specific_advice': 'Establish a core rhythmic motif and vary it in different sections.'
        })
        
        return suggestions
    
    def _get_structural_suggestions(self, analysis):
        """Generate structure-related suggestions"""
        suggestions = []
        
        structure_info = analysis.get('structure_analysis', {})
        total_measures = structure_info.get('total_measures', 0)
        sections = structure_info.get('sections', [])
        
        # Length suggestions
        if total_measures < 16:
            suggestions.append({
                'category': 'Song Length',
                'title': 'Extend song structure',
                'description': f'Your piece is {total_measures} measures long. Consider extending for a complete song.',
                'specific_advice': 'Add a bridge section, second verse, or instrumental break.'
            })
        elif total_measures > 100:
            suggestions.append({
                'category': 'Song Length',
                'title': 'Consider song focus',
                'description': f'Your piece is {total_measures} measures long. Consider if all sections are necessary.',
                'specific_advice': 'Edit for the strongest musical ideas or create an extended/short version.'
            })
        
        # Section variety
        if len(sections) < 3:
            suggestions.append({
                'category': 'Section Variety',
                'title': 'Add contrasting sections',
                'description': 'Consider adding more contrasting sections for musical interest.',
                'specific_advice': 'Try adding a bridge with different harmony, melody, or rhythm.'
            })
        
        # Common song forms
        suggestions.append({
            'category': 'Song Form',
            'title': 'Consider classic song forms',
            'description': 'Traditional song forms can provide effective structure.',
            'specific_advice': 'Try AABA, ABABCB (verse-chorus-bridge), or theme and variations.'
        })
        
        # Dynamic development
        suggestions.append({
            'category': 'Dynamic Arc',
            'title': 'Plan dynamic development',
            'description': 'Create an emotional journey through dynamic changes.',
            'specific_advice': 'Build intensity toward a climax, then provide resolution.'
        })
        
        return suggestions
    
    def _get_arrangement_ideas(self, analysis):
        """Generate arrangement and instrumentation ideas"""
        suggestions = []
        
        basic_info = analysis.get('basic_info', {})
        tracks = basic_info.get('tracks', 1)
        
        # Instrumentation suggestions
        if tracks == 1:
            suggestions.append({
                'category': 'Instrumentation',
                'title': 'Add accompanying instruments',
                'description': 'Your piece uses one track. Consider adding accompaniment.',
                'specific_advice': 'Add bass line, chord accompaniment, or percussion to support the melody.'
            })
        elif tracks > 8:
            suggestions.append({
                'category': 'Arrangement Focus',
                'title': 'Consider arrangement clarity',
                'description': f'Your piece uses {tracks} tracks. Ensure each part has a clear role.',
                'specific_advice': 'Consider which instruments play in which sections for clarity and impact.'
            })
        
        # Texture suggestions
        suggestions.append({
            'category': 'Texture Variety',
            'title': 'Vary musical texture',
            'description': 'Different sections can use different textural approaches.',
            'specific_advice': 'Try solo melody, harmony, counterpoint, or unison sections for contrast.'
        })
        
        # Production ideas
        suggestions.append({
            'category': 'Production Ideas',
            'title': 'Consider production elements',
            'description': 'Modern production can enhance your musical ideas.',
            'specific_advice': 'Add reverb for space, compression for punch, or effects for character.'
        })
        
        # Genre-specific suggestions
        suggestions.append({
            'category': 'Genre Elements',
            'title': 'Explore genre characteristics',
            'description': 'Different genres have characteristic arrangement elements.',
            'specific_advice': 'Research arrangement techniques from genres that inspire you.'
        })
        
        return suggestions
    
    def _get_development_strategies(self, analysis):
        """Generate overall development strategies"""
        strategies = []
        
        # Motivic development
        strategies.append({
            'category': 'Motivic Development',
            'title': 'Develop musical motifs',
            'description': 'Take short musical ideas and develop them throughout the piece.',
            'specific_advice': 'Use techniques like sequence, inversion, augmentation, or fragmentation.'
        })
        
        # Harmonic rhythm
        strategies.append({
            'category': 'Harmonic Development',
            'title': 'Vary harmonic rhythm',
            'description': 'Change how often chords change in different sections.',
            'specific_advice': 'Slow harmonic rhythm for verses, faster for choruses, or vice versa.'
        })
        
        # Call and response
        strategies.append({
            'category': 'Interactive Elements',
            'title': 'Use call and response',
            'description': 'Create dialogue between different instruments or sections.',
            'specific_advice': 'Have melody answered by harmony, or different instruments trading phrases.'
        })
        
        # Layering
        strategies.append({
            'category': 'Textural Building',
            'title': 'Build through layering',
            'description': 'Add instruments progressively to build energy and complexity.',
            'specific_advice': 'Start simple and add elements each section or phrase.'
        })
        
        # Contrast
        strategies.append({
            'category': 'Musical Contrast',
            'title': 'Use contrast effectively',
            'description': 'Contrast in dynamics, rhythm, harmony, or texture creates interest.',
            'specific_advice': 'Follow loud with soft, complex with simple, high with low.'
        })
        
        return strategies
    
    def _suggest_chord_extensions(self, key, mode, existing_chords):
        """Suggest specific chord extensions"""
        scale_notes = self.music_theory.get_scale_notes(key, mode)
        
        suggestions = []
        if scale_notes:
            # Suggest diatonic chords not yet used
            for i, note in enumerate(scale_notes):
                chord_type = self.music_theory.major_chords[i] if mode == 'major' else self.music_theory.minor_chords[i]
                suggested_chord = f"{note} {chord_type}"
                
                if not any(note in existing for existing in existing_chords):
                    suggestions.append(suggested_chord)
        
        return f"Try adding: {', '.join(suggestions[:3])}" if suggestions else "Explore diatonic chords in your key."
    
    def _suggest_secondary_dominants(self, key, mode):
        """Suggest secondary dominant chords"""
        scale_notes = self.music_theory.get_scale_notes(key, mode)
        
        if not scale_notes:
            return "Explore dominant chords that resolve to scale degrees."
        
        # Common secondary dominants
        suggestions = []
        if len(scale_notes) >= 6:
            suggestions.append(f"V/vi: Dominant of {scale_notes[5]} (adds tension)")
            suggestions.append(f"V/V: Dominant of {scale_notes[4]} (classic preparation)")
            suggestions.append(f"V/ii: Dominant of {scale_notes[1]} (smooth voice leading)")
        
        return '; '.join(suggestions) if suggestions else "Try dominant chords that resolve to different scale degrees."
    
    def _suggest_modal_interchange(self, key):
        """Suggest modal interchange chords"""
        minor_scale = self.music_theory.get_scale_notes(key, 'minor')
        
        if not minor_scale:
            return "Try borrowing chords from the parallel minor key."
        
        suggestions = [
            f"iv chord: {minor_scale[3]} minor (borrowed from {key} minor)",
            f"♭VII chord: {minor_scale[6]} major (borrowed from {key} minor)",
            f"♭VI chord: {minor_scale[5]} major (borrowed from {key} minor)"
        ]
        
        return '; '.join(suggestions)

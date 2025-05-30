// Global variables to store analysis results
let currentAnalysis = null;
let currentRecommendations = null;

// DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const removeFileBtn = document.getElementById('removeFile');
const uploadForm = document.getElementById('uploadForm');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingSection = document.getElementById('loadingSection');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
});

function setupEventListeners() {
    // File upload area interactions
    if (uploadArea) {
        uploadArea.addEventListener('click', () => fileInput?.click());
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleDrop);
    }

    // File input change
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }

    // Remove file button
    if (removeFileBtn) {
        removeFileBtn.addEventListener('click', clearFile);
    }

    // Form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleFormSubmit);
    }

    // Analysis goal checkboxes
    const goalCheckboxes = document.querySelectorAll('input[name="goals"]');
    goalCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', handleGoalChange);
    });

    // Genre selection checkbox
    const genreGoal = document.getElementById('goalGenre');
    if (genreGoal) {
        genreGoal.addEventListener('change', handleGenreGoalChange);
    }

    // Auto-improve checkbox
    const autoImproveCheckbox = document.getElementById('autoImprove');
    if (autoImproveCheckbox) {
        autoImproveCheckbox.addEventListener('change', handleAutoImproveChange);
    }
}

function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (isValidMidiFile(file)) {
            fileInput.files = files;
            displayFileInfo(file);
        } else {
            showError('Please select a valid MIDI file (.mid or .midi)');
        }
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        if (isValidMidiFile(file)) {
            displayFileInfo(file);
            hideError();
        } else {
            showError('Please select a valid MIDI file (.mid or .midi)');
            clearFile();
        }
    }
}

function isValidMidiFile(file) {
    const validExtensions = ['.mid', '.midi'];
    const fileName = file.name.toLowerCase();
    return validExtensions.some(ext => fileName.endsWith(ext));
}

function displayFileInfo(file) {
    if (fileName) {
        fileName.textContent = `${file.name} (${formatFileSize(file.size)})`;
    }
    if (fileInfo) {
        fileInfo.style.display = 'block';
    }
    
    // Show analysis goals section
    const analysisGoals = document.getElementById('analysisGoals');
    if (analysisGoals) {
        analysisGoals.style.display = 'block';
        analysisGoals.classList.add('fade-in');
    }
    
    // Show auto-improve section
    const autoImproveSection = document.getElementById('autoImproveSection');
    if (autoImproveSection) {
        autoImproveSection.style.display = 'block';
        autoImproveSection.classList.add('fade-in');
    }
    
    if (analyzeBtn) {
        analyzeBtn.disabled = false;
    }
}

function clearFile() {
    if (fileInput) {
        fileInput.value = '';
    }
    if (fileInfo) {
        fileInfo.style.display = 'none';
    }
    
    // Hide analysis goals section
    const analysisGoals = document.getElementById('analysisGoals');
    if (analysisGoals) {
        analysisGoals.style.display = 'none';
    }
    
    // Hide auto-improve section
    const autoImproveSection = document.getElementById('autoImproveSection');
    if (autoImproveSection) {
        autoImproveSection.style.display = 'none';
    }
    
    if (analyzeBtn) {
        analyzeBtn.disabled = true;
    }
    hideError();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function displayImprovedMidiSection(improvedMidi, userPreferences) {
    const section = document.getElementById('improvedMidiSection');
    const appliedImprovements = document.getElementById('appliedImprovements');
    const downloadBtn = document.getElementById('downloadImprovedBtn');
    const filenameDisplay = document.getElementById('improvedFilename');
    
    if (!section) return;
    
    // Show the section
    section.style.display = 'block';
    section.classList.add('fade-in');
    
    // Display applied improvements based on user goals
    if (appliedImprovements && userPreferences.goals) {
        const goalDescriptions = {
            'harmony': '<i class="fas fa-layer-group text-success me-2"></i>Enhanced chord progressions and harmonic movement',
            'melody': '<i class="fas fa-wave-square text-success me-2"></i>Improved melodic lines and harmonic intervals',
            'rhythm': '<i class="fas fa-drum text-success me-2"></i>Added rhythmic elements and percussion tracks',
            'structure': '<i class="fas fa-sitemap text-success me-2"></i>Extended song structure with intro/outro sections',
            'arrangement': '<i class="fas fa-magic text-success me-2"></i>Enhanced instrumentation and accompaniment',
            'genre': '<i class="fas fa-music text-success me-2"></i>Applied genre-specific styling and characteristics'
        };
        
        let improvementsHTML = '';
        userPreferences.goals.forEach(goal => {
            if (goalDescriptions[goal]) {
                improvementsHTML += `<li class="mb-1">${goalDescriptions[goal]}</li>`;
            }
        });
        
        if (userPreferences.target_genre) {
            improvementsHTML += `<li class="mb-1"><i class="fas fa-guitar text-success me-2"></i>Optimized for ${userPreferences.target_genre} style</li>`;
        }
        
        appliedImprovements.innerHTML = improvementsHTML;
    }
    
    // Set filename
    if (filenameDisplay) {
        filenameDisplay.textContent = improvedMidi.filename || 'improved_music.mid';
    }
    
    // Set up download functionality
    if (downloadBtn) {
        downloadBtn.onclick = function() {
            downloadImprovedMidi(improvedMidi.download_id, improvedMidi.filename);
        };
    }
}

function downloadImprovedMidi(downloadId, filename) {
    const downloadBtn = document.getElementById('downloadImprovedBtn');
    
    if (downloadBtn) {
        // Show loading state
        const originalHTML = downloadBtn.innerHTML;
        downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Preparing Download...';
        downloadBtn.disabled = true;
        
        // Create download link
        const downloadUrl = `/download/${downloadId}`;
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Restore button after a delay
        setTimeout(() => {
            downloadBtn.innerHTML = originalHTML;
            downloadBtn.disabled = false;
            
            // Optionally clean up the temporary file after download
            setTimeout(() => {
                fetch(`/cleanup/${downloadId}`, { method: 'POST' })
                    .catch(error => console.log('Cleanup completed'));
            }, 5000); // Clean up after 5 seconds
        }, 1000);
    }
}

function handleGoalChange(e) {
    const goalOption = e.target.closest('.analysis-goal-option');
    if (goalOption) {
        if (e.target.checked) {
            goalOption.classList.add('checked');
        } else {
            goalOption.classList.remove('checked');
        }
    }
}

function handleGenreGoalChange(e) {
    const genreSelection = document.getElementById('genreSelection');
    if (genreSelection) {
        if (e.target.checked) {
            genreSelection.style.display = 'block';
        } else {
            genreSelection.style.display = 'none';
        }
    }
}

function handleAutoImproveChange(e) {
    const analyzeBtnText = document.getElementById('analyzeBtnText');
    if (analyzeBtnText) {
        if (e.target.checked) {
            analyzeBtnText.textContent = 'Analyze & Generate Improved MIDI';
        } else {
            analyzeBtnText.textContent = 'Analyze & Get Recommendations';
        }
    }
}

function handleFormSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData();
    const file = fileInput?.files[0];
    
    if (!file) {
        showError('Please select a MIDI file');
        return;
    }
    
    formData.append('file', file);
    
    // Show loading state
    showLoading();
    hideError();
    
    // Upload and analyze file
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        
        if (data.success) {
            currentAnalysis = data.analysis;
            currentRecommendations = data.recommendations;
            
            // Store results in sessionStorage for the results page
            sessionStorage.setItem('analysisResults', JSON.stringify({
                analysis: currentAnalysis,
                recommendations: currentRecommendations,
                filename: data.filename
            }));
            
            // Redirect to results page
            window.location.href = '/results';
        } else {
            showError(data.error || 'An error occurred during analysis');
        }
    })
    .catch(error => {
        hideLoading();
        console.error('Error:', error);
        showError('Failed to analyze file. Please try again.');
    });
}

function showLoading() {
    if (loadingSection) {
        loadingSection.style.display = 'block';
    }
    if (analyzeBtn) {
        analyzeBtn.disabled = true;
    }
}

function hideLoading() {
    if (loadingSection) {
        loadingSection.style.display = 'none';
    }
    if (analyzeBtn && fileInput?.files[0]) {
        analyzeBtn.disabled = false;
    }
}

function showError(message) {
    if (errorMessage) {
        errorMessage.textContent = message;
    }
    if (errorSection) {
        errorSection.style.display = 'block';
    }
}

function hideError() {
    if (errorSection) {
        errorSection.style.display = 'none';
    }
}

// Results page functions
function loadResults() {
    const resultsContainer = document.getElementById('resultsContainer');
    const loadingResults = document.getElementById('loadingResults');
    const noResults = document.getElementById('noResults');
    
    // Get results from sessionStorage
    const storedResults = sessionStorage.getItem('analysisResults');
    
    if (storedResults) {
        try {
            const results = JSON.parse(storedResults);
            currentAnalysis = results.analysis;
            currentRecommendations = results.recommendations;
            
            // Hide loading and show results
            if (loadingResults) {
                loadingResults.style.display = 'none';
            }
            if (resultsContainer) {
                resultsContainer.style.display = 'block';
                displayResults(results);
            }
        } catch (error) {
            console.error('Error parsing results:', error);
            showNoResults();
        }
    } else {
        showNoResults();
    }
}

function showNoResults() {
    const resultsContainer = document.getElementById('resultsContainer');
    const loadingResults = document.getElementById('loadingResults');
    const noResults = document.getElementById('noResults');
    
    if (loadingResults) {
        loadingResults.style.display = 'none';
    }
    if (resultsContainer) {
        resultsContainer.style.display = 'none';
    }
    if (noResults) {
        noResults.style.display = 'block';
    }
}

function displayResults(results) {
    // Display improved MIDI download section if available
    if (results.improved_midi && results.improved_midi.available) {
        displayImprovedMidiSection(results.improved_midi, results.user_preferences);
    }
    
    displayAnalysisSummary(results.analysis);
    displayDetailedAnalysis(results.analysis);
    displayRecommendations(results.recommendations);
}

function displayAnalysisSummary(analysis) {
    const summaryContainer = document.getElementById('analysisSummary');
    if (!summaryContainer) return;
    
    const keyInfo = analysis.key_signature || {};
    const tempoInfo = analysis.tempo_info || {};
    const notesInfo = analysis.notes_analysis || {};
    const basicInfo = analysis.basic_info || {};
    
    const summaryHTML = `
        <div class="row">
            <div class="col-md-3 col-sm-6 mb-3">
                <div class="analysis-item text-center">
                    <div class="analysis-label">Key Signature</div>
                    <div class="analysis-value h5">${keyInfo.key || 'Unknown'}</div>
                </div>
            </div>
            <div class="col-md-3 col-sm-6 mb-3">
                <div class="analysis-item text-center">
                    <div class="analysis-label">Tempo</div>
                    <div class="analysis-value h5">${tempoInfo.average_bpm || 120} BPM</div>
                </div>
            </div>
            <div class="col-md-3 col-sm-6 mb-3">
                <div class="analysis-item text-center">
                    <div class="analysis-label">Total Notes</div>
                    <div class="analysis-value h5">${notesInfo.total_notes || 0}</div>
                </div>
            </div>
            <div class="col-md-3 col-sm-6 mb-3">
                <div class="analysis-item text-center">
                    <div class="analysis-label">Tracks</div>
                    <div class="analysis-value h5">${basicInfo.tracks || 0}</div>
                </div>
            </div>
        </div>
    `;
    
    summaryContainer.innerHTML = summaryHTML;
}

function displayDetailedAnalysis(analysis) {
    displayBasicAnalysis(analysis.basic_info, analysis.tempo_info);
    displayHarmonyAnalysis(analysis.key_signature, analysis.chord_progression);
    displayMelodyAnalysis(analysis.melodic_analysis, analysis.notes_analysis);
    displayRhythmAnalysis(analysis.rhythm_patterns, analysis.tempo_info);
    displayStructureAnalysis(analysis.structure_analysis);
}

function displayBasicAnalysis(basicInfo, tempoInfo) {
    const container = document.getElementById('basicAnalysis');
    if (!container) return;
    
    const html = `
        <div class="row">
            <div class="col-md-6">
                <h5><i class="fas fa-info-circle me-2"></i>File Information</h5>
                <div class="analysis-item">
                    <div class="analysis-label">MIDI Format</div>
                    <div class="analysis-value">Type ${basicInfo?.format || 'Unknown'}</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-label">Number of Tracks</div>
                    <div class="analysis-value">${basicInfo?.tracks || 0}</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-label">Ticks Per Beat</div>
                    <div class="analysis-value">${basicInfo?.ticks_per_beat || 'Unknown'}</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-label">Duration</div>
                    <div class="analysis-value">${formatDuration(basicInfo?.length_seconds || 0)}</div>
                </div>
            </div>
            <div class="col-md-6">
                <h5><i class="fas fa-clock me-2"></i>Tempo Information</h5>
                <div class="analysis-item">
                    <div class="analysis-label">Average BPM</div>
                    <div class="analysis-value">${tempoInfo?.average_bpm || 120}</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-label">Tempo Changes</div>
                    <div class="analysis-value">${tempoInfo?.tempo_changes || 0}</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-label">Tempo Stability</div>
                    <div class="analysis-value">${tempoInfo?.tempo_stability || 'Unknown'}</div>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

function displayHarmonyAnalysis(keyInfo, chordInfo) {
    const container = document.getElementById('harmonyAnalysis');
    if (!container) return;
    
    const chords = chordInfo?.chords || [];
    const chordsDisplay = chords.length > 0 ? chords.slice(0, 8).join(', ') : 'No chords detected';
    
    const html = `
        <div class="row">
            <div class="col-md-6">
                <h5><i class="fas fa-key me-2"></i>Key Analysis</h5>
                <div class="analysis-item">
                    <div class="analysis-label">Detected Key</div>
                    <div class="analysis-value">${keyInfo?.key || 'Unknown'}</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-label">Mode</div>
                    <div class="analysis-value">${keyInfo?.mode || 'Unknown'}</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-label">Confidence</div>
                    <div class="analysis-value">${Math.round((keyInfo?.confidence || 0) * 100)}%</div>
                </div>
            </div>
            <div class="col-md-6">
                <h5><i class="fas fa-layer-group me-2"></i>Chord Analysis</h5>
                <div class="analysis-item">
                    <div class="analysis-label">Total Chords</div>
                    <div class="analysis-value">${chordInfo?.total_chords || 0}</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-label">Progression Type</div>
                    <div class="analysis-value">${chordInfo?.progression_type || 'Unknown'}</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-label">Detected Chords</div>
                    <div class="analysis-value">${chordsDisplay}</div>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

function displayMelodyAnalysis(melodyInfo, notesInfo) {
    const container = document.getElementById('melodyAnalysis');
    if (!container) return;
    
    const pitchRange = notesInfo?.pitch_range || {};
    const commonNotes = notesInfo?.most_common_notes || [];
    
    const html = `
        <div class="row">
            <div class="col-md-6">
                <h5><i class="fas fa-wave-square me-2"></i>Melodic Characteristics</h5>
                <div class="analysis-item">
                    <div class="analysis-label">Melodic Contour</div>
                    <div class="analysis-value">${melodyInfo?.contour || 'Unknown'}</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-label">Melodic Range</div>
                    <div class="analysis-value">${melodyInfo?.range || 0} semitones</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-label">Average Interval</div>
                    <div class="analysis-value">${melodyInfo?.average_interval || 0} semitones</div>
                </div>
            </div>
            <div class="col-md-6">
                <h5><i class="fas fa-music me-2"></i>Note Information</h5>
                <div class="analysis-item">
                    <div class="analysis-label">Pitch Range</div>
                    <div class="analysis-value">MIDI ${pitchRange.lowest || 0} - ${pitchRange.highest || 0}</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-label">Average Velocity</div>
                    <div class="analysis-value">${notesInfo?.average_velocity || 0}</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-label">Most Common Notes</div>
                    <div class="analysis-value">${commonNotes.slice(0, 5).join(', ') || 'None detected'}</div>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

function displayRhythmAnalysis(rhythmInfo, tempoInfo) {
    const container = document.getElementById('rhythmAnalysis');
    if (!container) return;
    
    const html = `
        <div class="row">
            <div class="col-md-6">
                <h5><i class="fas fa-drum me-2"></i>Rhythmic Patterns</h5>
                <div class="analysis-item">
                    <div class="analysis-label">Time Signature</div>
                    <div class="analysis-value">${rhythmInfo?.time_signature || '4/4'}</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-label">Rhythmic Complexity</div>
                    <div class="analysis-value">${rhythmInfo?.rhythmic_complexity || 'Unknown'}</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-label">Unique Durations</div>
                    <div class="analysis-value">${rhythmInfo?.unique_durations || 0}</div>
                </div>
            </div>
            <div class="col-md-6">
                <h5><i class="fas fa-tachometer-alt me-2"></i>Tempo Details</h5>
                <div class="analysis-item">
                    <div class="analysis-label">BPM Classification</div>
                    <div class="analysis-value">${classifyTempo(tempoInfo?.average_bpm || 120)}</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-label">Tempo Stability</div>
                    <div class="analysis-value">${tempoInfo?.tempo_stability || 'Unknown'}</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-label">Tempo Changes</div>
                    <div class="analysis-value">${tempoInfo?.tempo_changes || 0}</div>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

function displayStructureAnalysis(structureInfo) {
    const container = document.getElementById('structureAnalysis');
    if (!container) return;
    
    const sections = structureInfo?.sections || [];
    const sectionsHTML = sections.map(section => 
        `<span class="badge bg-primary me-2 mb-2">${section.name} (${section.measures})</span>`
    ).join('');
    
    const html = `
        <div class="row">
            <div class="col-md-6">
                <h5><i class="fas fa-sitemap me-2"></i>Song Structure</h5>
                <div class="analysis-item">
                    <div class="analysis-label">Total Measures</div>
                    <div class="analysis-value">${structureInfo?.total_measures || 0}</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-label">Estimated Form</div>
                    <div class="analysis-value">${structureInfo?.estimated_form || 'Unknown'}</div>
                </div>
                <div class="analysis-item">
                    <div class="analysis-label">Number of Sections</div>
                    <div class="analysis-value">${sections.length}</div>
                </div>
            </div>
            <div class="col-md-6">
                <h5><i class="fas fa-puzzle-piece me-2"></i>Detected Sections</h5>
                <div class="analysis-item">
                    <div class="analysis-label">Sections</div>
                    <div class="analysis-value">
                        ${sectionsHTML || '<span class="text-muted">No sections detected</span>'}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendationsAccordion');
    if (!container) return;
    
    const sections = [
        { key: 'harmonic_suggestions', title: 'Harmonic Suggestions', icon: 'fas fa-layer-group' },
        { key: 'melodic_suggestions', title: 'Melodic Suggestions', icon: 'fas fa-wave-square' },
        { key: 'rhythmic_suggestions', title: 'Rhythmic Suggestions', icon: 'fas fa-drum' },
        { key: 'structural_suggestions', title: 'Structural Suggestions', icon: 'fas fa-sitemap' },
        { key: 'arrangement_ideas', title: 'Arrangement Ideas', icon: 'fas fa-magic' },
        { key: 'development_strategies', title: 'Development Strategies', icon: 'fas fa-lightbulb' }
    ];
    
    let accordionHTML = '';
    
    sections.forEach((section, index) => {
        const items = recommendations[section.key] || [];
        if (items.length === 0) return;
        
        const itemsHTML = items.map(item => `
            <div class="recommendation-card">
                <div class="recommendation-category">${item.category}</div>
                <div class="recommendation-title">${item.title}</div>
                <p class="mb-2">${item.description}</p>
                <div class="text-muted"><strong>Suggestion:</strong> ${item.specific_advice}</div>
            </div>
        `).join('');
        
        accordionHTML += `
            <div class="accordion-item">
                <h2 class="accordion-header" id="heading${index}">
                    <button class="accordion-button ${index === 0 ? '' : 'collapsed'}" type="button" 
                            data-bs-toggle="collapse" data-bs-target="#collapse${index}" 
                            aria-expanded="${index === 0 ? 'true' : 'false'}" aria-controls="collapse${index}">
                        <i class="${section.icon} me-2"></i>
                        ${section.title} (${items.length})
                    </button>
                </h2>
                <div id="collapse${index}" class="accordion-collapse collapse ${index === 0 ? 'show' : ''}" 
                     aria-labelledby="heading${index}" data-bs-parent="#recommendationsAccordion">
                    <div class="accordion-body">
                        ${itemsHTML}
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = accordionHTML;
}

// Helper functions
function formatDuration(seconds) {
    if (!seconds) return '0:00';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

function classifyTempo(bpm) {
    if (bpm < 60) return 'Very Slow (Largo)';
    if (bpm < 80) return 'Slow (Adagio)';
    if (bpm < 100) return 'Moderate (Andante)';
    if (bpm < 120) return 'Medium (Moderato)';
    if (bpm < 140) return 'Fast (Allegro)';
    if (bpm < 180) return 'Very Fast (Presto)';
    return 'Extremely Fast';
}

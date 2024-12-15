function renderSong(songDict, semitones) {
    const songContainer = document.getElementById('song-content');
    let htmlContent = ''; // Start with an empty string

    let inChorus = false; // Track whether we're inside a chorus section

    songDict.forEach(section => {
        section.forEach(item => {
            if (item.directive) {
                switch (item.directive) {
                    case "{soc}":
                        if (!inChorus) {
                            htmlContent += `<div class="chorus">`;
                            inChorus = true;
                        }
                        break;
                    case "{eoc}":
                        if (inChorus) {
                            htmlContent += `</div>`;
                            inChorus = false;
                        }
                        break;
                }
            } else if (item.chord !== undefined) {
                const transposedChord = item.chord ? transposeChord(item.chord, semitones) : '';
                const chordSpan = transposedChord ? `<span class="chord">[${transposedChord}]</span>` : '';
                const lyricSpan = item.lyric ? `<span class="lyric">${item.lyric}</span>` : '';
                htmlContent += `<span class="line">${chordSpan} ${lyricSpan}</span>`;
            } else if (item.format === 'LINEBREAK') {
                htmlContent += '<br>';
            } else if (item.format === 'PARAGRAPHBREAK') {
                htmlContent += '<br><br>'; // Extra break for paragraph separation
            }
        });
        
    });

    // Ensure any unclosed section is properly closed
    if (inChorus) {
        htmlContent += `</div>`;
    }

    songContainer.innerHTML = htmlContent; // Set the complete HTML
}

function toggleChordBox(isVisible) {
    const chordContainer = document.getElementById('chord-container');
    if (isVisible) {
        chordContainer.classList.remove('d-none');
        updateChordPosition('bottom'); // Ensure default position is set to bottom
    } else {
        chordContainer.classList.add('d-none');
    }
}

async function renderChords() {
    const container = document.getElementById('bottom-chord-container');

    // Clear existing diagrams
    container.innerHTML = '';
    console.log("Clearing chord container and rendering new diagrams...");

    for (const chordName of uniqueChords) {
        console.log(`Processing chord: ${chordName}`);
        const chordData = await Raphael.chord.find(chordName, 1); // Ensure async handling of find()

        if (!chordData) {
            console.warn(`Chord not found: ${chordName}`);
            continue;
        }

        // Create a container for the chord diagram
        const diagramContainer = document.createElement('div');
        diagramContainer.className = 'chord-diagram';

        // Render the chord
        const chord = new Raphael.chord.Chord(diagramContainer, chordData, chordName);
        container.appendChild(diagramContainer);
    }

    console.log("All chords rendered successfully!");
}

function updateChordPosition(position) {
    // List of all placeholders
    const placeholders = [
        'top-chord-diagram-placeholder',
        'bottom-chord-diagram-placeholder',
        'left-chord-diagram-placeholder',
        'right-chord-diagram-placeholder'
    ];

    // Hide all placeholders
    placeholders.forEach(placeholderId => {
        const placeholder = document.getElementById(placeholderId);
        placeholder.classList.add('d-none');
    });

    // Find the selected placeholder
    const selectedPlaceholder = document.getElementById(`${position}-chord-diagram-placeholder`);
    if (selectedPlaceholder) {
        selectedPlaceholder.classList.remove('d-none'); // Make it visible
    } else {
        console.warn(`Placeholder for position "${position}" not found.`);
        return; // Exit if the placeholder doesn't exist
    }

    // Append the chord container to the selected placeholder
    const chordContainer = document.getElementById('chord-container');
    if (chordContainer) {
        selectedPlaceholder.appendChild(chordContainer);
        chordContainer.classList.remove('d-none'); // Ensure visibility
    } else {
        console.error("Chord container not found.");
        return; // Exit if the chord container doesn't exist
    }

    // Adjust layout for top and bottom positions
    if (position === 'top' || position === 'bottom') {
        chordContainer.classList.add('horizontal');
        chordContainer.classList.remove('vertical');
        chordContainer.style.display = 'flex';
        chordContainer.style.flexDirection = 'row'; // Horizontal layout
        chordContainer.style.flexWrap = 'wrap'; // Allow wrapping
        chordContainer.style.justifyContent = 'center'; // Center-align
    } else {
        // Reset layout for left and right positions
        chordContainer.classList.add('vertical');
        chordContainer.classList.remove('horizontal');
        chordContainer.style.display = 'flex';
        chordContainer.style.flexDirection = 'column'; // Vertical layout
        chordContainer.style.flexWrap = 'nowrap';
        chordContainer.style.justifyContent = 'flex-start'; // Align to top/left
    }

    // Dynamically adjust lyrics-container
    adjustLyricsContainer(position);
}

function adjustLyricsContainer(position) {
    const lyricsContainer = document.getElementById('lyrics-container');
    if (!lyricsContainer) {
        console.warn('Lyrics container not found.');
        return;
    }

    if (position === 'left' || position === 'right') {
        // Shrink lyrics container for left/right positioning
        lyricsContainer.style.flex = '0 0 70%'; // 70% width
    } else {
        // Expand lyrics container for top/bottom positioning
        lyricsContainer.style.flex = '1 1 auto'; // Full width
    }
}

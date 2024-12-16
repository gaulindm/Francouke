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
        updateChordPHPosition('bottom'); // Ensure default position is set to bottom
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

function printDiv(divId) {
    const contentElement = document.getElementById(divId);

    if (!contentElement) {
        console.error(`Element with ID "${divId}" not found.`);
        return;
    }

    // Clone the content to manipulate it safely
    const clonedContent = contentElement.cloneNode(true);

    // Check visibility of the bottom chords inline
    const bottomPlaceholder = clonedContent.querySelector("#bottom-chord-diagram-placeholder");
    const isBottomVisible = bottomPlaceholder && 
        window.getComputedStyle(bottomPlaceholder).display !== "none" && 
        bottomPlaceholder.offsetWidth > 0 && 
        bottomPlaceholder.offsetHeight > 0;

    if (!isBottomVisible) {
        console.log("Bottom chord placeholder is hidden and will not be included in the print view.");
        if (bottomPlaceholder) bottomPlaceholder.remove(); // Remove if hidden
    } else {
        console.log("Bottom chord placeholder is visible and will be included in the print view.");
        if (bottomPlaceholder) {
            const chordContainer = bottomPlaceholder.querySelector("#bottom-chord-container");
            if (chordContainer) {
                // Apply styles to position chords at the bottom page margin
                bottomPlaceholder.style.position = "fixed";
                bottomPlaceholder.style.bottom = "20px"; // Space from the bottom edge
                bottomPlaceholder.style.left = "0";
                bottomPlaceholder.style.width = "100%";
                bottomPlaceholder.style.backgroundColor = "white"; // Ensure visibility on colored backgrounds

                chordContainer.style.display = "flex";
                chordContainer.style.flexDirection = "row";
                chordContainer.style.justifyContent = "center";
                chordContainer.style.alignItems = "center";
                chordContainer.style.gap = "10px";
                chordContainer.style.flexWrap = "wrap"; // Wrap if too many chords
            }
        }
    }

    // Open a new print window
    const printWindow = window.open("", "", "height=600,width=800");
    if (!printWindow) {
        console.error("Unable to open print window.");
        return;
    }

    // Write content into the print window
    printWindow.document.write("<html><head><title>Print Score</title>");
    printWindow.document.write("<style>");
    printWindow.document.write(`
        body { font-family: Arial, sans-serif; margin: 20px; }
        #song_header { width: 100%; border-collapse: collapse; }
        #song_header td { padding: 5px; text-align: center; }
        .verse, .chorus { margin: 20px 0; padding: 10px; }
        .verse { background-color: #e9f7e9; border-left: 4px solid #28a745; }
        .chorus { background-color: #fff3cd; border-left: 4px solid #ffc107; }
        #bottom-chord-container { display: flex; justify-content: center; align-items: center; gap: 10px; flex-wrap: wrap; }
        #bottom-chord-diagram-placeholder { position: fixed; bottom: 20px; left: 0; width: 100%; background-color: white; }
        .chord-diagram { margin: 5px; width: 100px; height: 120px; border: 1px solid #ccc; }
        @media print { 
            .verse, .chorus { page-break-inside: avoid; }
            #bottom-chord-diagram-placeholder { position: fixed; bottom: 20px; left: 0; width: 100%; }
        }
    `);
    printWindow.document.write("</style></head><body>");
    printWindow.document.write(clonedContent.innerHTML);
    printWindow.document.write("</body></html>");
    printWindow.document.close();

    // Trigger print
    printWindow.print();
}

function transposeChord(chord, semitones) {
    const chordRegex = /^([A-G][#b]?)(m|M|maj|min|dim|aug|sus|add|7|9|11|13)?$/;
    const match = chord.match(chordRegex);

    if (!match) {
        return chord; // Return the original chord if it doesn't match the expected pattern
    }

    const baseChord = match[1];
    const chordType = match[2] || '';

    const newValue = (chordMap[baseChord] + semitones + 12) % 12;

    return reverseChordMap[newValue] + chordType;
}


function transposeSong(semitones) {
    renderSong(songDict, parseInt(semitones));
}

function updateChordPHPosition(position) {
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
        if (placeholder) {
            placeholder.classList.add('d-none');
        }
    });

    // Handle "None" option
    if (position === 'none') {
        // Hide the chord container if it exists
        const chordContainer = document.getElementById('chord-container');
        if (chordContainer) {
            chordContainer.classList.add('d-none');
        } else {
            console.error("Chord container not found.");
        }
        // Adjust lyrics-container for no chords
        adjustLyricsContainer(position);
        return; // Exit early since no further action is needed
    }

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

document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('printPreviewModal');

    modal.addEventListener('show.bs.modal', function () {
        // Populate the modal song header and lyrics
        document.getElementById('modal-song-header').innerHTML = document.getElementById('song_header').outerHTML;
        document.getElementById('modal-lyrics-container').innerHTML = document.getElementById('song-content').innerHTML;

        // Define modal placeholders
        const modalPlaceholders = {
            top: document.getElementById('modal-top-chord-placeholder'),
            bottom: document.getElementById('modal-bottom-chord-placeholder'),
            left: document.getElementById('modal-left-chord-placeholder'),
            right: document.getElementById('modal-right-chord-placeholder'),
        };

        // Define main view placeholders
        const mainPlaceholders = {
            top: document.getElementById('top-chord-diagram-placeholder'),
            bottom: document.getElementById('bottom-chord-diagram-placeholder'),
            left: document.getElementById('left-chord-diagram-placeholder'),
            right: document.getElementById('right-chord-diagram-placeholder'),
        };

        // Clear all modal placeholders
        Object.values(modalPlaceholders).forEach(placeholder => {
            placeholder.innerHTML = ''; // Clear content
            placeholder.classList.add('d-none'); // Hide by default
        });

        // Populate modal placeholders from the main view
        Object.keys(mainPlaceholders).forEach(position => {
            const mainPlaceholder = mainPlaceholders[position];
            const modalPlaceholder = modalPlaceholders[position];

            if (mainPlaceholder && mainPlaceholder.innerHTML.trim()) {
                // Copy content to the corresponding modal placeholder
                modalPlaceholder.innerHTML = mainPlaceholder.innerHTML;
                modalPlaceholder.classList.remove('d-none'); // Show the placeholder

                // Apply layout-specific classes
                if (position === 'top' || position === 'bottom') {
                    modalPlaceholder.classList.add('horizontal');
                    modalPlaceholder.classList.remove('vertical');
                } else {
                    modalPlaceholder.classList.add('vertical');
                    modalPlaceholder.classList.remove('horizontal');
                }
            }
        });

        console.log('Modal placeholders populated successfully.');
    });
});

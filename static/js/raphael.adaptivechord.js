(function (Raphael) {
    // Define the Raphael.chord namespace
    Raphael.chord = {
        data: null, // To store loaded chord data
    };

    /**
     * Load chord data from a specific JSON file.
     * @param {string} url - Path to the JSON file.
     * @returns {Promise<void>} - Resolves when data is loaded successfully.
     */
    Raphael.chord.loadData = async function (url) {
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const jsonData = await response.json();
            Raphael.chord.data = jsonData;
            console.log("Chord data loaded successfully:", jsonData);
        } catch (error) {
            console.error("Failed to load chord data:", error);
            Raphael.chord.data = null; // Clear existing data on failure
        }
    };

    /**
     * Find a chord by instrument, root, type, and variation.
     * @param {string} instrument - Name of the instrument.
     * @param {string} root - Root note of the chord.
     * @param {string} name - Chord type (e.g., maj, min).
     * @param {number} variation - Variation number (1-based index).
     * @returns {Array|undefined} - Chord data array or undefined if not found.
     */
 
    Raphael.chord.find = function (instrument, root, name, variation) {
        if (!Raphael.chord.data) {
            console.error("Chord data not loaded. Please load data using loadData method.");
            return undefined;
        }
    
        const instrumentData = Raphael.chord.data.chords;
        if (!instrumentData) {
            console.error(`Instrument data not found.`);
            return undefined;
        }
    
        // Default to 'maj' if no chord type is provided
        if (!name || name.trim() === "") {
            name = "maj";
        }
    
        const chord = instrumentData.find(c => c.root === root);
        if (!chord) {
            console.error(`Chord root ${root} not found.`);
            return undefined;
        }
    
        const type = chord.types.find(t => t.name === name);
        if (!type) {
            console.error(`Chord type ${name} not found for root ${root}.`);
            return undefined;
        }
    
        if (!variation || variation < 1) {
            variation = 1;
        }
    
        if (variation > type.variations.length) {
            console.warn(`Variation ${variation} exceeds available variations. Defaulting to last variation.`);
            variation = type.variations.length;
        }
    
        return type.variations[variation - 1];
    };
    

    // Chord constructor to render diagrams
    var Chord = function (elementOrPosition, data, labelOrVariant) {
        if (
            typeof elementOrPosition === 'object' &&
            elementOrPosition.x !== undefined &&
            elementOrPosition.y !== undefined
        ) {
            this.element = Raphael(
                elementOrPosition.x,
                elementOrPosition.y,
                100,
                120
            );
        } else {
            this.element = Raphael(elementOrPosition, 100, 120);
        }

        this.element.setViewBox(0, 0, 100, 120);

        const numStrings = data.length; // Determine the number of strings
        const fretCount = 5; // Fixed number of frets
        const fretboardWidth = 100; // Total width of the fretboard
        const fretboardHeight = 90; // Total height of the fretboard
        const stringSpacing = (fretboardWidth - 40) / (numStrings - 1); // Dynamic spacing between strings
        const fretSpacing = fretboardHeight / fretCount; // Fixed spacing between frets

        this.frets = [];
        this.strings = [];
        this.chordData = data;

        // Draw fretboard (frets and strings)
        for (let i = 0; i <= fretCount; i++) {
            const y = 30 + i * fretSpacing;
            this.element.path(`M20 ${y}L80 ${y}`); // Horizontal frets
        }
        const stringPositions = []; // Store X-positions of strings
        for (let i = 0; i < numStrings; i++) {
            const x = 20 + i * stringSpacing;
            stringPositions.push(x);
            this.element.path(`M${x} 30L${x} ${30 + fretboardHeight}`); // Vertical strings
        }

        // Calculate the lowest fret to adjust the diagram (offset for partial chords)
        const minFret = Math.min(...data.filter((f) => f > 0)) || 1; // Default to 1 if no frets are pressed
        const offset = minFret > 3 ? minFret - 1 : 0; // Offset only for frets > 3
       
        // Draw a thick nut line if no offset
        if (offset === 0) {
            this.element.path(`M20 30L80 30`).attr({
                'stroke-width': 3, // Thicker line
                stroke: '#000',
            });
        }

        // Draw chord positions
        data.forEach((fret, index) => {
            const x = stringPositions[index];

            if (fret === -1) {
                // Muted string
                this.element.text(x, 20, 'x');
            } else if (fret === 0) {
                // Open string
                this.element.circle(x, 23, 4).attr({ stroke: '#000', fill: '#fff' });
            } else {
                // Fretted note
                const y = 30 + (fret - offset) * fretSpacing - fretSpacing / 2;
                this.element.circle(x, y, 6).attr({ fill: '#000' });
            }
        });

        // Add fret position marker (if offset > 0 and not Infinity)
        if (offset > 0 && isFinite(offset)) {
            this.element.text(15, 45, `${offset + 1}fr`).attr({
                'font-size': 12,
                'text-anchor': 'middle',
            });
        } else {
            // Draw nut if offset is 0 or Infinity
            this.element.path('M20 30L80 30').attr({
                'stroke-width': 3,
                stroke: '#000',
            });
        }        

        

        // Add chord label
        if (labelOrVariant) {
            this.element.text(50, 8, labelOrVariant).attr({
                'font-size': 14,
                'font-weight': 'bold',
                'text-anchor': 'middle',
            });
        }
    };

    Chord.prototype.remove = function () {
        this.element.remove();
    };

    // Expose the Chord constructor
    Raphael.chord.Chord = Chord;

})(window.Raphael);

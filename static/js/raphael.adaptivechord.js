(function (Raphael) {
    Raphael.chord = {
        data: null, // Stores the chord data
        currentInstrument: "ukulele", // Default instrument
        isLefty: false, // Default lefty mode is off
        setInstrument: function (instrument) {
            this.currentInstrument = instrument;
        },
        toggleLeftyMode: function (isLefty) {
            this.isLefty = isLefty;
        },
        loadData: async function (filePath) {
            try {
                const response = await fetch(filePath);
                this.data = await response.json();
                console.log(`Chord data for ${this.currentInstrument} loaded successfully.`);
            } catch (error) {
                console.error(`Error loading chord data from ${filePath}:`, error);
            }
        },
        find: function (chordName, variation) {
            if (!this.data) {
                console.error("Chord data not loaded. Please call loadData first.");
                return undefined;
            }
        
            const chord = this.data.find((c) => c.name === chordName);
            if (!chord) {
                console.error(`Chord ${chordName} not found.`);
                return undefined;
            }
        
            variation = variation || 1; // Default to the first variation
            if (variation > chord.variations.length) {
                console.warn(`Variation ${variation} exceeds available variations. Using the last one.`);
                variation = chord.variations.length;
            }
        
            console.log(`Chord data for ${chordName} found:`, chord.variations[variation - 1]);
            return chord.variations[variation - 1];
        }
    };

    Raphael.chord.Chord = function (elementOrPosition, data, labelOrVariant) {
        const element = typeof elementOrPosition === 'string' || elementOrPosition instanceof HTMLElement
            ? Raphael(elementOrPosition, 80, 110) // Increased height from 90 to 110
            : Raphael(elementOrPosition.x, elementOrPosition.y, 80, 110);
    
        element.setViewBox(0, 0, 100, 140); // Increased viewBox height from 120 to 140
    
        const numStrings = data.length;
        const fretCount = 5; // Number of frets to display
        const fretboardWidth = 100;
        const fretboardHeight = 90; // Keep fretboard height the same
        const stringSpacing = (fretboardWidth - 40) / (numStrings - 1);
        const fretSpacing = fretboardHeight / fretCount;
    
        // Draw light border
        element.rect(0, 0, 100, 140).attr({
            stroke: '#ccc', // Light gray border color
            'stroke-width': 1, // Thin border
            fill: 'none', // Transparent fill
        });
    
        // Determine if an offset is needed
        const activeFrets = data.filter((fret) => fret > 0); // Exclude 0 and -1
        const minFret = Math.min(...activeFrets);
        const offset = minFret > 3 ? minFret : 0; // Only apply offset if all frets > 3
    
        // Draw strings
        const stringPositions = [];
        for (let i = 0; i < numStrings; i++) {
            const x = 20 + i * stringSpacing;
            stringPositions.push(Raphael.chord.isLefty ? 80 - (x - 20) : x); // Adjust for lefty
            element.path(`M${stringPositions[i]} 40L${stringPositions[i]} ${40 + fretboardHeight}`);
        }
    
        // Draw frets
        for (let i = 0; i <= fretCount; i++) {
            const y = 40 + i * fretSpacing;
            element.path(`M20 ${y}L80 ${y}`);
        }
    
        // Draw nut bar if there is no offset
        if (offset === 0) {
            const nutBarThickness = 4; // Thickness of the nut bar
            element.rect(20, 40 - nutBarThickness, 60, nutBarThickness).attr({
                fill: '#000', // Solid black color
                stroke: '#000', // Optional: Same color as the fill
                'stroke-width': 0, // No border
            });
        }
    
        // Add offset label if needed
        if (offset > 0) {
            element.text(2, 28, `${offset}fr`).attr({
                'font-size': 16,
                'font-weight': 'bold',
                'text-anchor': 'start',
            });
        }
    
        // Draw markers
        data.forEach((fret, index) => {
            const x = stringPositions[index];
            if (fret === -1) {
                element.text(x, 17, 'x').attr({
                    'font-size': 17,
                    'font-weight': 'normal',
                    'text-anchor': 'middle',
                    'fill': '#000',
                });
            } else if (fret === 0) {
                element.circle(x, 30, 4).attr({ stroke: '#000', fill: '#fff' });
            } else {
                const adjustedFret = fret - offset;
                if (adjustedFret > 0) {
                    const y = 40 + adjustedFret * fretSpacing - fretSpacing / 2;
                    element.circle(x, y, 5).attr({ fill: '#000' });
                }
            }
        });
    
        // Add optional label
        if (labelOrVariant) {
            element.text(50, 10, labelOrVariant).attr({
                'font-size': 24,
                'font-weight': 'bold',
                'text-anchor': 'middle',
            });
        }
    
        return { element }; // Return the Raphael instance
    };
    
         
    // Expose Raphael's chord functionality
    window.Raphael.chord = Raphael.chord;
})(window.Raphael);

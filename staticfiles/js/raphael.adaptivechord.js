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
            ? Raphael(elementOrPosition, 80, 90)
            : Raphael(elementOrPosition.x, elementOrPosition.y, 80, 90);
    
        element.setViewBox(0, 0, 100, 120); // Ensure proper sizing for the SVG viewport
    
        const numStrings = data.length;
        const fretCount = 5;
        const fretboardWidth = 100;
        const fretboardHeight = 90;
        const stringSpacing = (fretboardWidth - 40) / (numStrings - 1);
        const fretSpacing = fretboardHeight / fretCount;
    
        // Draw strings
        const stringPositions = [];
        for (let i = 0; i < numStrings; i++) {
            const x = 20 + i * stringSpacing;
            stringPositions.push(Raphael.chord.isLefty ? 80 - (x - 20) : x); // Adjust for lefty
            element.path(`M${stringPositions[i]} 30L${stringPositions[i]} ${30 + fretboardHeight}`);
        }
    
        // Draw frets
        for (let i = 0; i <= fretCount; i++) {
            const y = 30 + i * fretSpacing;
            element.path(`M20 ${y}L80 ${y}`);
        }
    
        // Draw markers
        data.forEach((fret, index) => {
            const x = stringPositions[index];
            if (fret === -1) {
                element.text(x, 20, 'x');
            } else if (fret === 0) {
                element.circle(x, 23, 4).attr({ stroke: '#000', fill: '#fff' });
            } else {
                const y = 30 + fret * fretSpacing - fretSpacing / 2;
                element.circle(x, y, 6).attr({ fill: '#000' });
            }
        });
    
        // Add optional label
        if (labelOrVariant) {
            element.text(50, 8, labelOrVariant).attr({
                'font-size': 20,
                'font-weight': 'bold',
                'text-anchor': 'middle',
            });
        }
    
        return { element }; // Return the Raphael instance
    };
    
    // Expose Raphael's chord functionality
    window.Raphael.chord = Raphael.chord;
})(window.Raphael);

(function (Raphael) {
    Raphael.chord = {
        data: null, // Stores the chord data
        currentInstrument: "ukulele", // Default instrument
        setInstrument: function (instrument) {
            this.currentInstrument = instrument;
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
    
            const chord = this.data.find(c => c.name === chordName);
            if (!chord) {
                console.error(`Chord ${chordName} not found.`);
                return undefined;
            }
    
            variation = variation || 1; // Default to the first variation
            if (variation > chord.variations.length) {
                console.warn(`Variation ${variation} exceeds available variations. Using the last one.`);
                variation = chord.variations.length;
            }
    
            return chord.variations[variation - 1];
        }
    };
    

    // Chord constructor
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

        // Rest of the constructor remains unchanged
        const numStrings = data.length; 
        const fretCount = 5; 
        const fretboardWidth = 100; 
        const fretboardHeight = 90; 
        const stringSpacing = (fretboardWidth - 40) / (numStrings - 1); 
        const fretSpacing = fretboardHeight / fretCount; 

        // Draw fretboard (frets and strings)
        for (let i = 0; i <= fretCount; i++) {
            const y = 30 + i * fretSpacing;
            this.element.path(`M20 ${y}L80 ${y}`); 
        }

        const stringPositions = []; 
        for (let i = 0; i < numStrings; i++) {
            const x = 20 + i * stringSpacing;
            stringPositions.push(x);
            this.element.path(`M${x} 30L${x} ${30 + fretboardHeight}`); 
        }

        const minFret = Math.min(...data.filter((f) => f > 0)) || 1; 
        const offset = minFret > 3 ? minFret - 1 : 0; 
       
        // Draw nut
        if (offset === 0) {
            this.element.path(`M20 30L80 30`).attr({
                'stroke-width': 3, 
                stroke: '#000',
            });
        }

        data.forEach((fret, index) => {
            const x = stringPositions[index];
            if (fret === -1) {
                this.element.text(x, 20, 'x');
            } else if (fret === 0) {
                this.element.circle(x, 23, 4).attr({ stroke: '#000', fill: '#fff' });
            } else {
                const y = 30 + (fret - offset) * fretSpacing - fretSpacing / 2;
                this.element.circle(x, y, 6).attr({ fill: '#000' });
            }
        });

        if (offset > 0 && isFinite(offset)) {
            this.element.text(15, 45, `${offset + 1}fr`).attr({
                'font-size': 12,
                'text-anchor': 'middle',
            });
        } else {
            this.element.path('M20 30L80 30').attr({
                'stroke-width': 3,
                stroke: '#000',
            });
        }        

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

    Raphael.chord.Chord = Chord;

})(window.Raphael);
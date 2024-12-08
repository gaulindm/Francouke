/*!
 * Ukulele Chord Diagram - Raphael Plugin
 * Adapted for 4-string diagrams (ukulele).
 */

(function (Raphael) {
    Raphael.chord = function (elementOrPosition, data, labelOrVariant) {
        return new Chord(elementOrPosition, data, labelOrVariant);
    };

    // Inline chord data for ukulele (C, F, G, Am)
    Raphael.chord.data = [
        {
            root: ['C'],
            types: [
                {
                    name: 'maj',
                    variations: [
                        [0, 0, 0, 3], // C major (open)
                    ],
                },
            ],
        },
        {
            root: ['F'],
            types: [
                {
                    name: 'maj',
                    variations: [
                        [2, 0, 1, 0], // F major (open)
                    ],
                },
            ],
        },
        {
            root: ['G'],
            types: [
                {
                    name: 'maj',
                    variations: [
                        [0, 2, 3, 2], // G major (open)
                    ],
                },
            ],
        },
        {
            root: ['A'],
            types: [
                {
                    name: 'min',
                    variations: [
                        [2, 0, 0, 0], // A minor (open)
                    ],
                },
            ],
        },
    ];

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

        const numStrings = data.length; // Determine the number of strings
        const fretCount = 5; // Fixed number of frets
        const fretboardWidth = 100; // Total width of the fretboard
        const fretboardHeight = 90; // Total height of the fretboard
        const stringSpacing = (fretboardWidth - 40)/ (numStrings - 1); // Dynamic spacing between strings
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
        const offset = minFret > 3 ? minFret - 1 : 0;  //Ofset only for frets > 3


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
                this.element.circle(x, 25, 4).attr({ stroke: '#000', fill: '#fff' });
            } else {
                // Fretted note
                const y = 30 + (fret - offset) * fretSpacing - fretSpacing / 2;
                this.element.circle(x, y, 6).attr({ fill: '#000' });
            }
        });


        // Add fret position marker (if offset > 0)
        if (offset > 0) {
            this.element.text(15, 45, `${offset + 1}fr`).attr({
                'font-size': 12 ,
                'text-anchor':'middle',
            });
        }

        // Add chord label
        if (labelOrVariant) {
            this.element.text(50, 12, labelOrVariant).attr({
                 'font-size': 14,
                 'font-weight':'bold',
                 'text-anchor':'middle',
                });
        }
    };

    Chord.prototype.remove = function () {
        this.element.remove();
    };
})(window.Raphael);

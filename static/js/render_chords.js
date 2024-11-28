// Load the JSON chord data
fetch('/static/data/chord_data_ukulele.json')
    .then((response) => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then((chordData) => {
        console.log("Loaded chord data:", chordData);

        // Render chords using Raphael.js
        renderChords(chordData);
    })
    .catch((error) => console.error("Error loading JSON:", error));

function renderChords(chords) {
    const canvas = document.getElementById('chordCanvas');

    // Create a Raphael canvas
    const paper = Raphael(canvas, 500, 500);

    let x = 10; // Starting x-coordinate
    let y = 10; // Starting y-coordinate
    const chordWidth = 100; // Width of each chord diagram
    const chordHeight = 120; // Height of each chord diagram

    // Iterate over each chord
    Object.entries(chords).forEach(([chordName, positions], index) => {
        // Draw the chord box
        const box = paper.rect(x, y, chordWidth, chordHeight);
        box.attr({
            stroke: "#000",
            "stroke-width": 2,
        });

        // Add the chord name
        paper.text(x + chordWidth / 2, y + 15, chordName).attr({
            "font-size": 16,
            "font-weight": "bold",
        });

        // Draw strings and frets
        for (let i = 0; i < 4; i++) {
            // Vertical strings
            paper.path(`M${x + 20 + i * 15},${y + 30}V${y + chordHeight - 10}`).attr({
                stroke: "#999",
            });
        }
        for (let j = 0; j < 4; j++) {
            // Horizontal frets
            paper.path(`M${x + 15},${y + 30 + j * 20}H${x + chordWidth - 15}`).attr({
                stroke: "#999",
            });
        }

        // Place the chord positions (dots)
        positions[0].split("").forEach((pos, stringIndex) => {
            const fret = parseInt(pos, 10); // Convert position to an integer
            if (fret > 0) {
                paper.circle(
                    x + 20 + stringIndex * 15, // X-coordinate
                    y + 30 + fret * 20 - 10, // Y-coordinate
                    5 // Circle radius
                ).attr({
                    fill: "#000",
                });
            }
        });

        // Update position for the next chord
        x += chordWidth + 20;
        if (x + chordWidth > 500) {
            x = 10;
            y += chordHeight + 20;
        }
    });
}

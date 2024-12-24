import subprocess
import os

def convert_abc_to_audio(abc_notation, output_dir="output"):
    # Create necessary file paths
    abc_file = os.path.join(output_dir, "melody.abc")
    midi_file = os.path.join(output_dir, "melody.mid")
    audio_file = os.path.join(output_dir, "melody.wav")
    
    # Save the ABC notation to a file
    os.makedirs(output_dir, exist_ok=True)
    with open(abc_file, "w") as f:
        f.write(abc_notation)

    # Convert ABC to MIDI using abcmidi
    subprocess.run(["abc2midi", abc_file, "-o", midi_file], check=True)

    # Convert MIDI to WAV using FluidSynth
    from midi2audio import FluidSynth
    fs = FluidSynth()
    fs.midi_to_audio(midi_file, audio_file)

    return audio_file

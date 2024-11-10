import json
from django.core.management.base import BaseCommand
from songbook.models import Instrument, Chord

class Command(BaseCommand):
    help = 'Load instrument and chord data from JSON files'

    def handle(self, *args, **kwargs):
        # Load instruments
        with open('data/instruments.json') as f:
            instruments_data = json.load(f)

        for instrument_data in instruments_data:
            instrument, created = Instrument.objects.get_or_create(
                name=instrument_data['name'],
                defaults={
                    'tuning': instrument_data['tuning'],
                    'alternate_names': instrument_data['alternate_names']
                }
            )

        # Load chords for each instrument
        for instrument in Instrument.objects.all():
            file_name = f"data/{instrument.name.lower().replace(' ', '_')}_chords.json"
            with open(file_name) as f:
                chords_data = json.load(f)

            for chord_name, positions in chords_data.items():
                Chord.objects.get_or_create(
                    instrument=instrument,
                    name=chord_name,
                    defaults={'positions': positions}
                )

        self.stdout.write(self.style.SUCCESS('Successfully loaded instrument and chord data'))

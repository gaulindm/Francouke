from django.db import models

class Instrument(models.Model):
    """
    Represents a musical instrument with a specific tuning.
    """
    name = models.CharField(max_length=100, unique=True)
    tuning = models.JSONField(
        help_text="List of strings tuning, e.g., ['G', 'C', 'E', 'A']"
    )

    def __str__(self):
        return self.name

class Chord(models.Model):
    """
    Represents a chord definition tied to an instrument.
    """
    name = models.CharField(max_length=100)
    instrument = models.ForeignKey(
        Instrument, related_name='chords', on_delete=models.CASCADE
    )
    frets = models.JSONField(
        help_text="List of fret positions for each string, e.g., [0, 0, 0, 3]"
    )
    fingers = models.JSONField(
        blank=True, null=True,
        help_text="List of finger positions, e.g., [1, 2, 3, 4]"
    )

    def __str__(self):
        return f"{self.name} ({self.instrument.name})"

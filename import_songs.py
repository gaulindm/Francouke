#Importing songs from a folder from shell
#Script provided by chatGPT

#As a temporary measure for testing, you can allow the contributor field to be null by updating your model:

#Change songbook/model.py

contributor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


#After modifying the model, run migrations:


#python manage.py makemigrations
#python manage.py migrate





#STEP 1:  Run following command in terminal
#python manage.py shell


#STEP 2: Copy and Paste following script




import os
from songbook.models import Song  # Replace 'yourapp' with the name of your Django app


# Define the directory containing your ChordPro files
chordpro_dir = 'mychordpro'


# Counter to track imported files
imported_count = 0

# Loop through all .txt files in the directory if your extension are different change line 27
for filename in os.listdir(chordpro_dir):
    if filename.endswith('.pro'):
        # Construct the full path to the file
        file_path = os.path.join(chordpro_dir, filename)
        
        # Open and read the file content
        with open(file_path, 'r') as file:
            chordpro_text = file.read()
            
            # Create a new Song instance with the file content
            song = Song(songChordPro=chordpro_text)
            song.save()
            
            # Increment the counter
            imported_count += 1
            print(f"Imported: {filename}")

# Print the total count of imported songs
print(f"Total songs imported: {imported_count}")

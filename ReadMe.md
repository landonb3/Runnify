## ReadMe - Runnify
### Description
Runnify calculates your precise running tempo and curates a Spotify playlist to match that tempo

### Installation Instruction
In the command line, change your directory to Runnify, and run the command `python manage.py runserver`. Then, create an account with your Spotify username and enjoy!

### Add to Spotify
Open a playlist and click on the button "Send to Spotify". Once you login with your Spotify credentials, and give Runnify permissions, you'll be redirected back to Runnify. Copy the redirected url, paste into the command line, and hit enter. After doing this once, each time you "Send to Spotify", you should see the new playlist appear in your saved music.

### Code Structure
This project is structured according to Django's standard view-model-controller. Runnify contains models for playlists and users. Views are created to handle the logic behind the interface in the model (adding playlists, publishing playlists, login/logout/signup, etc.). The controller is implemented with Python login in the HTML code, and post/get requests to views. 

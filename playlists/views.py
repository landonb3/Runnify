from django.shortcuts import render, redirect
import spotipy
from playlists.models import Playlist
from collections import Counter
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import requests
import random
import json

class Spotify:
    def __init__(self,request):
        self.client_id='da1d0e63b69d48b3a40751c12c4e2d43'
        self.client_secret='e6e21e552485498dae7de26c911d6a76'
        self.user_id = request.user.username
        self.redirect_uri = 'http://localhost:8000/home'
        self.token = None
        self.request = request

    def get_username(self,request):
        return self.user_id

    def get_public_api(self):
        client_credentials_manager = SpotifyClientCredentials(self.client_id,
                                                            self.client_secret)
        return spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    def get_private_api(self,scope):
        self.token = util.prompt_for_user_token(self.user_id, scope, self.client_id, self.client_secret, redirect_uri=self.redirect_uri)
        return spotipy.Spotify(auth=self.token)

    def get_token(self):
        return self.token

    def get_genres(self):
        return ['Acoustic', 'Afrobeat', 'Alt-rock', 'Alternative', 'Ambient', 'Anime', 'Black-metal', 'Bluegrass', 'Blues', 'Bossanova', 'Brazil', 'Breakbeat', 'British', 'Cantopop', 'Chicago-house', 'Children', 'Chill', 'Classical', 'Club', 'Comedy', 'Country', 'Dance', 'Dancehall', 'Death-metal', 'Deep-house', 'Detroit-techno', 'Disco', 'Disney', 'Drum-and-bass', 'Dub', 'Dubstep', 'Edm', 'Electro', 'Electronic', 'Emo', 'Folk', 'Forro', 'French', 'Funk', 'Garage', 'German', 'Gospel', 'Goth', 'Grindcore', 'Groove', 'Grunge', 'Guitar', 'Happy', 'Hard-rock', 'Hardcore', 'Hardstyle', 'Heavy-metal', 'Hip-hop', 'Holidays', 'Honky-tonk', 'House', 'Idm', 'Indian', 'Indie', 'Indie-pop', 'Industrial', 'Iranian', 'J-dance', 'J-idol', 'J-pop', 'J-rock', 'Jazz', 'K-pop', 'Kids', 'Latin', 'Latino', 'Malay', 'Mandopop', 'Metal', 'Metal-misc', 'Metalcore', 'Minimal-techno', 'Movies', 'Mpb', 'New-age', 'New-release', 'Opera', 'Pagode', 'Party', 'Philippines-opm', 'Piano', 'Pop', 'Pop-film', 'Post-dubstep', 'Power-pop', 'Progressive-house', 'Psych-rock', 'Punk', 'Punk-rock', 'R-n-b', 'Rainy-day', 'Reggae', 'Reggaeton', 'Road-trip', 'Rock', 'Rock-n-roll', 'Rockabilly', 'Romance', 'Sad', 'Salsa', 'Samba', 'Sertanejo', 'Show-tunes', 'Singer-songwriter', 'Ska', 'Sleep', 'Songwriter', 'Soul', 'Soundtracks', 'Spanish', 'Study', 'Summer', 'Swedish', 'Synth-pop', 'Tango', 'Techno', 'Trance', 'Trip-hop', 'Turkish', 'Work-out', 'World-music']

    def __eq__(self, other):
        return self.request == other.request
        
    def __str__(self):
        return "Spotofy Object with Client ID: " + self.client_id


# view managing how existing playlists are displayed
def playlist_view(request,id):
    if request.user.is_authenticated:
        # gets the playlist by id from the database, and prepares to communicate with the Spotify API
        playlist = Playlist.objects.get(id=id)
        songs_by_id = playlist.songs.split(',')[1:]
        sp = Spotify(request).get_public_api()
        song_features = []

        # analytics about playlist
        desired_tempo = str(playlist.tempo)
        desired_genre = playlist.genre
        num_songs = str(len(songs_by_id))

        # calculates playlist length
        millis = int(playlist.duration)
        minutes=str(int((millis/(1000*60))%60))
        hours=str(int((millis/(1000*60*60))%60))
        if len(minutes) == 1:
            minutes = '0' + minutes
        total_length = hours + ':' + minutes

        # gets features about each song from the Spotify API and adds to the song_features list
        for s in songs_by_id:
            t = sp.track(s)
            millis = int(t['duration_ms'])
            seconds=int((millis/1000)%60)
            if len(str(seconds)) == 1:
                seconds = '0' + str(seconds)
            minutes=int((millis/(1000*60))%60)
            song_features.append([t['name'], t['artists'][0]['name'], t['id'], str(minutes) + ':' + str(seconds),float(round(sp.audio_features([t['id']])[0]['tempo'],1)),t['external_urls']['spotify']])
        return render(request, 'playlist.html', {'playlist': playlist,'p':song_features, 'desired_tempo': desired_tempo,'desired_genre':desired_genre,'num_songs':num_songs,'total_length': total_length})
    return redirect('/home')

# view in charge of the what appears on a user's homepage
def home(request):
    if request.user.is_authenticated:
        # gets all playlists and calculates features of aggregate set
        playlists = Playlist.objects.all().filter(author=request.user).order_by('-time_created_at')
        num_playlists = playlists.count()
        all_tempos = 0
        all_genres = []
        average_tempo = 0
        for p in playlists:
            all_tempos += p.tempo
            all_genres.append(p.genre)
        if num_playlists == 0:
            most_common = 'N/A'
        else:
            most_common = Counter(all_genres).most_common(1)[0][0]
            average_tempo = int(all_tempos/num_playlists)
        return render(request, 'home.html', {"playlists": playlists, "num_playlists": num_playlists, "aver_tempo": average_tempo, "genre": most_common})
    return redirect('/home')

# view in charge of the what appears on a user's homepage
def create_playlist_view(request, id):
    s = Spotify(request)
    all_genres = s.get_genres()
    
    # numbers to fill in the drop downs
    count_sixty = []
    for i in range(0,60):
        if i < 10:
            count_sixty.append('0' + str(i))
        else:
            count_sixty.append(str(i))
    count_two = [str(i) for i in range(0,5)]
    count_twenty = [str(i) for i in range(4,21)]

    # 'new' describes the state of the page before drop downs are selected
    if id == "new":
        if request.method == "POST":
            
            if request.POST["pace_unit_chosen"] == "per Mile":
                pace_unit = "m"
            else:
                pace_unit = "km"

            # form has been completely filled out, meaning a new playlist should be created
            if 'final' in request.POST:
                tempo = 0
                velocity_min_per_km = 0
                if pace_unit == "km":
                    velocity_min_per_km = float(request.POST["mins_pace_chosen"]) + (float(request.POST["mins_pace_chosen"])/ 60.0)
                else:
                    velocity_min_per_km = (float(request.POST["mins_pace_chosen"]) + (float(request.POST["mins_pace_chosen"])/ 60.0)) * 0.621372

                # 3 different options for finding an individual's stride length
                # option 1, raw stride length
                if "stride_length" in request.POST:
                    try:
                        val = float(request.POST["stride_length"])
                        if val < 0.5:
                            return render(request, 'create.html', {'error': "Please enter a stride length value of at least 0.5","technique": 1, "title": request.POST["title"], "genre_types": all_genres, "genre": request.POST["genre"], "hours_length_chosen":request.POST["hours_length_chosen"][:-1],"hours_length":count_two,"mins_length_chosen":request.POST["mins_length_chosen"], "mins_length": count_sixty, "mins_pace_chosen":request.POST["mins_pace_chosen"], "mins_pace": count_twenty, "secs_pace_chosen":request.POST["secs_pace_chosen"], "secs_pace":count_sixty, "pace_unit_chosen": pace_unit})
                    except:
                        return render(request, 'create.html', {'error': "Please enter a stride length value of at least 0.5","technique": 1, "title": request.POST["title"], "genre_types": all_genres, "genre": request.POST["genre"], "hours_length_chosen":request.POST["hours_length_chosen"][:-1],"hours_length":count_two,"mins_length_chosen":request.POST["mins_length_chosen"], "mins_length": count_sixty, "mins_pace_chosen":request.POST["mins_pace_chosen"], "mins_pace": count_twenty, "secs_pace_chosen":request.POST["secs_pace_chosen"], "secs_pace":count_sixty, "pace_unit_chosen": pace_unit})
                    unit = request.POST.get("stride_length_units")
                    sl_km = 0
                    if unit == "inches":
                        sl_km = float(request.POST["stride_length"]) / 39.37 / 1000
                    elif unit == "feet":
                        sl_km = float(request.POST["stride_length"]) * 12 / 39.37 / 1000
                    elif unit == "centimeters":
                        sl_km = float(request.POST["stride_length"]) / 1000 / 100.0
                    else:
                        sl_km = float(request.POST["stride_length"]) / 1000
                    tempo = 1.0 / (sl_km * velocity_min_per_km)
                # option 2, estimate based on height
                elif "height" in request.POST:
                    try:
                        val = float(request.POST["height"])
                        if val <= 0:
                            return render(request, 'create.html', {'error': "Please enter a positive height","technique": 2, "title": request.POST["title"], "genre_types": all_genres, "genre": request.POST["genre"], "hours_length_chosen":request.POST["hours_length_chosen"][:-1],"hours_length":count_two,"mins_length_chosen":request.POST["mins_length_chosen"], "mins_length": count_sixty, "mins_pace_chosen":request.POST["mins_pace_chosen"], "mins_pace": count_twenty, "secs_pace_chosen":request.POST["secs_pace_chosen"], "secs_pace":count_sixty, "pace_unit_chosen": pace_unit})
                    except:
                        return render(request, 'create.html', {'error': "Please enter a positive height","technique": 2, "title": request.POST["title"], "genre_types": all_genres, "genre": request.POST["genre"], "hours_length_chosen":request.POST["hours_length_chosen"][:-1],"hours_length":count_two,"mins_length_chosen":request.POST["mins_length_chosen"], "mins_length": count_sixty, "mins_pace_chosen":request.POST["mins_pace_chosen"], "mins_pace": count_twenty, "secs_pace_chosen":request.POST["secs_pace_chosen"], "secs_pace":count_sixty, "pace_unit_chosen": pace_unit})
                    unit = request.POST.get("height_units")
                    height_km = 0
                    if unit == "inches":
                        height_km = float(request.POST["height"]) / 1000 / 39.37
                    elif unit == "feet":
                        height_km = float(request.POST["height"]) * 12 / 1000 / 39.37
                    elif unit == "centimeters":
                        height_km = float(request.POST["height"]) / 1000 / 100.0
                    else:
                        height_km = float(request.POST["height"]) / 1000
                    gender = request.POST["gender_chosen"]
                    scaling_factor = 0
                    if gender is "male":
                        scaling_factor = 0.415 * 2
                    else:
                        scaling_factor = 0.413 * 2
                    sl_km = height_km * scaling_factor
                    tempo = 1 / (sl_km * velocity_min_per_km)
                # option 3, determined tempo entered
                else:
                    try:
                        val = int(request.POST["tempo"])
                        if val < 60 or val > 200:
                            return render(request, 'create.html', {'error': "Please enter an interger tempo between 60 and 200","technique": 3, "title": request.POST["title"], "genre_types": all_genres, "genre": request.POST["genre"], "hours_length_chosen":request.POST["hours_length_chosen"][:-1],"hours_length":count_two,"mins_length_chosen":request.POST["mins_length_chosen"], "mins_length": count_sixty, "mins_pace_chosen":request.POST["mins_pace_chosen"], "mins_pace": count_twenty, "secs_pace_chosen":request.POST["secs_pace_chosen"], "secs_pace":count_sixty, "pace_unit_chosen": pace_unit})
                    except:
                        return render(request, 'create.html', {'error': "Please enter an interger tempo between 60 and 200","technique": 3, "title": request.POST["title"], "genre_types": all_genres, "genre": request.POST["genre"], "hours_length_chosen":request.POST["hours_length_chosen"][:-1],"hours_length":count_two,"mins_length_chosen":request.POST["mins_length_chosen"], "mins_length": count_sixty, "mins_pace_chosen":request.POST["mins_pace_chosen"], "mins_pace": count_twenty, "secs_pace_chosen":request.POST["secs_pace_chosen"], "secs_pace":count_sixty, "pace_unit_chosen": pace_unit})
                    tempo = val
                genre = request.POST["genre"]
                title = request.POST["title"]

                # access the Spotify API to get recommendations based on tempo and genre
                sp = s.get_public_api()
                results = sp.recommendations(seed_genres =[genre.lower()], limit=100, min_tempo=int(tempo)-3, max_tempo=int(tempo)+3, target_tempo=int(tempo), country='US')
                
                # adds recommended tracks to the playlist, until playlist length is met
                play = []
                for t in results['tracks']:
                    play.append([t['name'], t['artists'][0]['name'], t['id'], t['duration_ms'],sp.audio_features([t['id']])[0]['tempo']])
                random.shuffle(play)
                songs = ''
                mins_length = 0
                if request.POST["mins_length_chosen"][0] == '0':
                    mins_length = int(request.POST["mins_length_chosen"][1])
                else:
                    mins_length = int(request.POST["mins_length_chosen"])
                tot_ms = int(request.POST["hours_length_chosen"][:1])*3600000 + mins_length*60000
                dur_ms = 0
                for s in play:
                    if dur_ms <= tot_ms:
                        songs += ',' + s[2]
                        dur_ms += s[3]
                    else:
                        break
                if len(title) == 0:
                    title = "Default Title"

                # creates the playlist object and adds it to the database
                p = Playlist.objects.create(songs=songs, author=request.user, playlist_name=title, genre=genre, tempo=str(int(tempo)), duration=dur_ms, title=title)
                return redirect("/playlist" + '/' + str(p.id))
            else:
                # drop down has been selected, so page should be updated with selected option
                if '1' in request.POST:
                    technique = 1
                elif '2' in request.POST:
                    technique = 2
                else:  
                    technique = 3    
                return render(request, 'create.html', {"technique": technique, "title": request.POST["title"], "genre_types": all_genres, "genre": request.POST["genre"], "hours_length_chosen":request.POST["hours_length_chosen"][:-1],"hours_length":count_two,"mins_length_chosen":request.POST["mins_length_chosen"], "mins_length": count_sixty, "mins_pace_chosen":request.POST["mins_pace_chosen"], "mins_pace": count_twenty, "secs_pace_chosen":request.POST["secs_pace_chosen"], "secs_pace":count_sixty, "pace_unit_chosen": pace_unit})
        else:
            return render(request, 'create.html', {"technique": 0, "genre_types": all_genres,"hours_length":count_two, "mins_length": count_sixty, "mins_pace": count_twenty, "secs_pace":count_sixty, "pace_unit_chosen": "m"})   
    else:
        return redirect("/home")

def publish_view(request):
    # gets the playlist
    p = Playlist.objects.get(id=request.GET['id'])
    songs_by_id = p.songs.split(',')[1:]
    s = Spotify(request)
    username = s.get_username(request)
    sp = s.get_private_api('playlist-modify-private')
    token = s.get_token()

    # compiles a list of songs in the playlist in a list by uri
    uris = []
    for s in songs_by_id:
        t = sp.track(s)
        uris.append(t['uri'])

    # creates the playlist for the user using the Spotify API
    endpoint_url = f"https://api.spotify.com/v1/users/{username}/playlists"
    request_body = json.dumps({
            "name": p.title,
            "description": str(p.tempo) + " BPM - " + str(p.genre) + " - Playlist created by Runnify",
            "public": False
            })
    response = requests.post(url = endpoint_url, data = request_body, headers={"Content-Type":"application/json", 
                            "Authorization":f"Bearer {token}"})
    if response.status_code in [200,201]:
        playlist_id = response.json()['id']
        endpoint_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        request_body = json.dumps({
            "uris" : uris
            })
        response = requests.post(url = endpoint_url, data = request_body, headers={"Content-Type":"application/json", 
                            "Authorization":f"Bearer {token}"})
    return redirect("/home")

# deletes playlist by finding the playlist in the database and removing from the database
def delete_view(request):
    p = Playlist.objects.get(id=request.GET['id'])
    p.delete()
    return redirect('/home')

# walks a user through how to connect their Runnify account to Spotify
def connect_to_spotify_view(request):
    if request.method == "POST":
        s = Spotify(request)
        username = s.get_username(request)
        sp = s.get_private_api('playlist-modify-private')
        token = s.get_token()
        endpoint_url = f"https://api.spotify.com/v1/users/{username}/playlists"
        request_body = json.dumps({
            })
        response = requests.post(url = endpoint_url, data = request_body, headers={"Content-Type":"application/json", 
                            "Authorization":f"Bearer {token}"})
        return redirect("/home")
    return render(request, 'connect_to_spotify.html', {}) 
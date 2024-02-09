import spotipy
from spotipy.oauth2 import SpotifyOAuth
from random import randint
import random

# Initialize Spotipy client with user authentication
def initialize_spotify_client():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="bbff0e095ce94643a1c8d1136824dbfa",
                                                     client_secret="0efd5f03128e480c9213e99d44947425",
                                                     redirect_uri="http://localhost:5000/callback",
                                                     scope="user-library-read playlist-modify-private"))

# Get related artists for a given artist
def get_related_artists(sp, artist_id):
    related_artists = []
    results = sp.artist_related_artists(artist_id)
    for artist in results["artists"]:
        related_artists.append(artist["id"])
    return related_artists

# Get artists by genre
def get_artists_by_genre(sp, genre):
    artists = []
    results = sp.search(q='genre:"{}"'.format(genre), type='artist', limit=50)
    for artist in results['artists']['items']:
        artists.append(artist['id'])
    return artists

# Create a playlist with top tracks from a specific artist
def create_playlist_artist(sp, user_id, playlist_name, num_songs, artist_id):
    # Create an empty playlist
    playlist_id = sp.user_playlist_create(user_id, playlist_name, public=False)["id"]

    # Get the top tracks for the artist
    top_tracks = sp.artist_top_tracks(artist_id)
    tracks = [track["id"] for track in top_tracks["tracks"]]

    # Shuffle the tracks
    random.shuffle(tracks)

    # Add the desired number of songs to the playlist
    num_tracks = min(num_songs, len(tracks))
    sp.playlist_add_items(playlist_id, tracks[:num_tracks])

    print(f"Playlist '{playlist_name}' with {num_tracks} songs created successfully!")

    return tracks[:num_tracks], playlist_id

# Create a playlist with top tracks from related artists
def create_playlist(sp, user_id, playlist_name, num_songs, related_artists):
    # Create an empty playlist
    playlist_id = sp.user_playlist_create(user_id, playlist_name, public=False)["id"]

    # Get the top tracks for each related artist
    tracks = [] 
    for artist_id in related_artists:
        top_tracks = sp.artist_top_tracks(artist_id)
        tracks += [track["id"] for track in top_tracks["tracks"]]

    # Shuffle the tracks
    random.shuffle(tracks)

    # Add the desired number of songs to the playlist
    num_tracks = min(num_songs, len(tracks))
    sp.playlist_add_items(playlist_id, tracks[:num_tracks])

    print(f"Playlist '{playlist_name}' with {num_tracks} songs created successfully!")

    return tracks[:num_tracks], playlist_id

# Create a playlist with top tracks from multiple artists of a given genre
def create_playlist_genre(sp, user_id, playlist_name, num_songs, artists):
    # Create an empty playlist
    playlist_id = sp.user_playlist_create(user_id, playlist_name, public=False)["id"]

    # Collect tracks from multiple artists
    tracks = []
    for artist_id in artists:
        top_tracks = sp.artist_top_tracks(artist_id)
        tracks += [track["id"] for track in top_tracks["tracks"]]

    # Shuffle the tracks
    random.shuffle(tracks)

    # Add the desired number of songs to the playlist
    num_tracks = min(num_songs, len(tracks))
    sp.playlist_add_items(playlist_id, tracks[:num_tracks])

    print(f"Playlist '{playlist_name}' with {num_tracks} songs created successfully!")

    return tracks[:num_tracks], playlist_id

# Remove a track from the playlist by its index
def remove_track_from_playlist(sp, playlist_id, playlist_tracks, index, removed_tracks):
    track_id_to_remove = playlist_tracks.pop(index - 1)  # Adjust index to 0-based
    sp.playlist_remove_all_occurrences_of_items(playlist_id, [track_id_to_remove])  # Remove track from Spotify playlist on the server
    removed_tracks.append(track_id_to_remove)  # Add removed track to removed_tracks list
    return playlist_tracks, removed_tracks

def undo_redo_track(sp, playlist_id, playlist_tracks, removed_tracks, redo_tracks, action):
    if action == "undo":
        if removed_tracks:
            removed_track_id = removed_tracks.pop()  # Get the last removed track ID
            sp.playlist_add_items(playlist_id, [removed_track_id])  # Add the track back to the playlist on Spotify
            playlist_tracks.append(removed_track_id)  # Add the track back to the playlist_tracks list
            print("Track removal undone successfully!")
        else:
            print("No track to undo.")
    elif action == "redo":
        if redo_tracks:
            redo_track_id = redo_tracks.pop()  # Get the last removed track ID
            sp.playlist_add_items(playlist_id, [redo_track_id])  # Add the track back to the playlist on Spotify
            playlist_tracks.append(redo_track_id)  # Add the track back to the playlist_tracks list
            print("Track redo successful!")
        else:
            print("No track to redo.")
    return playlist_tracks, removed_tracks, redo_tracks

# Ask user if they want to upload to Spotify
def ask_to_upload(sp):
    ask_to_upload = input("Would you like to upload to Spotify? (Yes/No): ")

    return ask_to_upload.lower() == "yes"

def view_generated_playlist(sp, playlist_id):
    playlist_info = sp.playlist(playlist_id)
    print("\n\nGenerated Playlist:")
    print(f"Name: {playlist_info['name']}")
    print("Tracks:")
    for i, track in enumerate(playlist_info['tracks']['items'], start=1):
        print(f"{i}. {track['track']['name']} by {', '.join([artist['name'] for artist in track['track']['artists']])}")

# Add a song to the playlist
def add_song_to_playlist(sp, playlist_id):
    song_name = input("Enter the name of the song you want to add: ")
    results = sp.search(q=song_name, limit=1, type="track")
    if results['tracks']['items']:
        track_id = results['tracks']['items'][0]['id']
        sp.playlist_add_items(playlist_id, [track_id])
        print(f"Song '{song_name}' added to the playlist successfully!")
    else:
        print(f"No song found with the name '{song_name}'.")

def main():
    print("\n\nWELCOME TO THE SPOTIFY PLAYLIST GENERATOR APPLCIATION!")
    print("\nDo you want to create a playlist in no time? Well you are in luck!")
    print("This application will do just that! It will even take less time than manually creating a playlist on the app itself!") 
    print("Have fun and enjoy!\n")
    while True:
        print("\nMenu:")
        print("1. Create a playlist through related artists")
        print("2. Create a playlist by artist")
        print("3. Create a playlist by genre")
        print("4. HOW TO INSTRUCTIONS")
        print("5. Exit")

        # Prompt user to choose an option
        choice = input("\nChoose an option: ")

        if choice == "1":
            # Initialize Spotify client
            sp = initialize_spotify_client()

            # Prompt user to input artist name
            artist_name = input("Enter artist name: ")

            # Search for the artist using the Spotipy client
            results = sp.search(q=artist_name, limit=1, type="artist")
            if not results["artists"]["items"]:
                print(f"No artist found with name '{artist_name}'.")
            else:
                # Get the related artists and select one at random
                artist_id = results["artists"]["items"][0]["id"]
                related_artists = get_related_artists(sp, artist_id)
                random_artist_id = related_artists[randint(0, len(related_artists)-1)]

                playlist_name = f"{artist_name} Playlist"

                # Prompt user to input number of songs
                num_songs = int(input("Enter number of songs: "))

                # Create the playlist
                user_id = sp.me()["id"]
                playlist_tracks, playlist_id = create_playlist(sp, user_id, playlist_name, num_songs, related_artists)
                
                removed_tracks = []  # List to store removed tracks
                redo_tracks = []  # List to store redo tracks
                upload_choice = False  # Flag to track if the user chose to upload

                print("\nYour playlist has now been created! You may edit your playlist by adding, removing, or backtracking with the undo/redo feature.")
                print("However, keep in note that editing  the generated playlist does cost excessive time and effort...")
                print("But if you'd like to avoid make any desired changes to the generated playlist, no worries! You can upload the playlist straight to your Spotify!")

                while True:
                    # Display menu of options
                    print("\nMenu:")
                    print("1. Remove Track")
                    print("2. Undo/Redo")
                    print("3. Upload")
                    print("4. Generate Another Playlist")
                    print("5. View Generated Playlist")
                    print("6. Add Song")
                    print("7. Exit")

                    # Prompt user to choose an option
                    choice = input("Choose the task you want to do: ")

                    # Perform the selected task
                    if choice == "1":
                        track_index_to_remove = int(input("Enter the index of the track you want to remove: "))
                        playlist_tracks, removed_tracks = remove_track_from_playlist(sp, playlist_id, playlist_tracks, track_index_to_remove, removed_tracks)
                    elif choice == "2":
                        action = input("Enter 'undo' to undo the last removal or 'redo' to redo: ")
                        playlist_tracks, removed_tracks, redo_tracks = undo_redo_track(sp, playlist_id, playlist_tracks, removed_tracks, redo_tracks, action)
                    elif choice == "3":
                        if ask_to_upload(sp):
                            print("Playlist uploaded successfully!")
                            upload_choice = True  # Set flag to True if user chooses to upload
                        else:
                            print("Playlist not uploaded.")
                        break
                    elif choice == "4":
                        break
                    elif choice == "5":
                        if playlist_id:  # Check if a playlist has been generated
                            view_generated_playlist(sp, playlist_id)
                        else:
                            print("No playlist has been generated yet.")
                    elif choice == "6":
                        add_song_to_playlist(sp, playlist_id)
                    elif choice == "7":
                        # Delete playlist and exit
                        sp.playlist_remove_all_occurrences_of_items(playlist_id, playlist_tracks)
                        sp.user_playlist_unfollow(sp.me()["id"], playlist_id)
                        print("Playlist deleted successfully!")
                        return
                    else:
                        print("Invalid choice. Please choose a valid option.")

                # If the user did not choose to upload, delete the playlist
                if not upload_choice:
                    sp.playlist_remove_all_occurrences_of_items(playlist_id, playlist_tracks)
                    sp.user_playlist_unfollow(sp.me()["id"], playlist_id)
                    print("Playlist deleted successfully!\n\n")

                generate_another = input("Would you like to generate another playlist? (Yes/No): ")
                if generate_another.lower() != "yes":
                    break

        elif choice == "2":
            # Initialize Spotify client
            sp = initialize_spotify_client()

            # Prompt user to input artist name
            artist_name = input("Enter artist name: ")

            # Search for the artist using the Spotipy client
            results = sp.search(q=artist_name, limit=1, type="artist")
            if not results["artists"]["items"]:
                print(f"No artist found with name '{artist_name}'.")
            else:
                # Get the artist ID
                artist_id = results["artists"]["items"][0]["id"]
                artist_name = results["artists"]["items"][0]["name"]

                playlist_name = f"{artist_name} Playlist"

                # Prompt user to input number of songs
                num_songs = int(input("Enter number of songs: "))

                # Create the playlist
                user_id = sp.me()["id"]
                playlist_tracks, playlist_id = create_playlist_artist(sp, user_id, playlist_name, num_songs, artist_id)
                
                removed_tracks = []  # List to store removed tracks
                redo_tracks = []  # List to store redo tracks
                upload_choice = False  # Flag to track if the user chose to upload

                print("\nYour playlist has now been created! You may edit your playlist by adding, removing, or backtracking with the undo/redo feature.")
                print("However, keep in note that editing  the generated playlist does cost excessive time and effort...")
                print("But if you'd like to avoid make any desired changes to the generated playlist, no worries! You can upload the playlist straight to your Spotify!")

                while True:
                    # Display menu of options
                    print("\nMenu:")
                    print("1. Remove Track")
                    print("2. Undo/Redo")
                    print("3. Upload")
                    print("4. Generate Another Playlist")
                    print("5. View Generated Playlist")
                    print("6. Add Song")
                    print("7. Exit")

                    # Prompt user to choose an option
                    choice = input("Choose the task you want to do: ")

                    # Perform the selected task
                    if choice == "1":
                        track_index_to_remove = int(input("Enter the index of the track you want to remove: "))
                        playlist_tracks, removed_tracks = remove_track_from_playlist(sp, playlist_id, playlist_tracks, track_index_to_remove, removed_tracks)
                    elif choice == "2":
                        action = input("Enter 'undo' to undo the last removal or 'redo' to redo: ")
                        playlist_tracks, removed_tracks, redo_tracks = undo_redo_track(sp, playlist_id, playlist_tracks, removed_tracks, redo_tracks, action)
                    elif choice == "3":
                        if ask_to_upload(sp):
                            print("Playlist uploaded successfully!")
                            upload_choice = True  # Set flag to True if user chooses to upload
                        else:
                            print("Playlist not uploaded.")
                        break
                    elif choice == "4":
                        break
                    elif choice == "5":
                        if playlist_id:  # Check if a playlist has been generated
                            view_generated_playlist(sp, playlist_id)
                        else:
                            print("No playlist has been generated yet.")
                    elif choice == "6":
                        add_song_to_playlist(sp, playlist_id)
                    elif choice == "7":
                        # Delete playlist and exit
                        sp.playlist_remove_all_occurrences_of_items(playlist_id, playlist_tracks)
                        sp.user_playlist_unfollow(sp.me()["id"], playlist_id)
                        print("Playlist deleted successfully!")
                        return
                    else:
                        print("Invalid choice. Please choose a valid option.")

                # If the user did not choose to upload, delete the playlist
                if not upload_choice:
                    sp.playlist_remove_all_occurrences_of_items(playlist_id, playlist_tracks)
                    sp.user_playlist_unfollow(sp.me()["id"], playlist_id)
                    print("Playlist deleted successfully!")

                generate_another = input("Would you like to generate another playlist? (Yes/No): ")
                if generate_another.lower() != "yes":
                    break

        elif choice == "3":
            # Initialize Spotify client
            sp = initialize_spotify_client()

            # Prompt user to input genre
            genre = input("Enter genre: ")

            # Get artists by genre
            artists = get_artists_by_genre(sp, genre)
            if not artists:
                print(f"No artists found for genre '{genre}'.")
            else:
                # Select a random artist
                random_artist_id = random.choice(artists)
                artist_info = sp.artist(random_artist_id)
                artist_name = artist_info['name']

                playlist_name = f"{genre.capitalize()} Playlist"

                # Prompt user to input number of songs
                num_songs = int(input("Enter number of songs: "))

                # Create the playlist
                user_id = sp.me()["id"]
                playlist_tracks, playlist_id = create_playlist_genre(sp, user_id, playlist_name, num_songs, artists)
                
                removed_tracks = []  # List to store removed tracks
                redo_tracks = []  # List to store redo tracks
                upload_choice = False  # Flag to track if the user chose to upload

                print("\nYour playlist has now been created! You may edit your playlist by adding, removing, or backtracking with the undo/redo feature.")
                print("However, keep in note that editing  the generated playlist does cost excessive time and effort...")
                print("But if you'd like to avoid make any desired changes to the generated playlist, no worries! You can upload the playlist straight to your Spotify!")

                while True:
                    # Display menu of options
                    print("\nMenu:")
                    print("1. Remove Track")
                    print("2. Undo/Redo")
                    print("3. Upload")
                    print("4. Generate Another Playlist")
                    print("5. View Generated Playlist")
                    print("6. Add Song")
                    print("7. Exit")

                    # Prompt user to choose an option
                    choice = input("Choose the task you want to do: ")

                    # Perform the selected task
                    if choice == "1":
                        track_index_to_remove = int(input("Enter the index of the track you want to remove: "))
                        playlist_tracks, removed_tracks = remove_track_from_playlist(sp, playlist_id, playlist_tracks, track_index_to_remove, removed_tracks)
                    elif choice == "2":
                        action = input("Enter 'undo' to undo the last removal or 'redo' to redo: ")
                        playlist_tracks, removed_tracks, redo_tracks = undo_redo_track(sp, playlist_id, playlist_tracks, removed_tracks, redo_tracks, action)
                    elif choice == "3":
                        if ask_to_upload(sp):
                            print("Playlist uploaded successfully!")
                            upload_choice = True  # Set flag to True if user chooses to upload
                        else:
                            print("Playlist not uploaded.")
                        break
                    elif choice == "4":
                        break
                    elif choice == "5":
                        if playlist_id:  # Check if a playlist has been generated
                            view_generated_playlist(sp, playlist_id)
                        else:
                            print("No playlist has been generated yet.")
                    elif choice == "6":
                        add_song_to_playlist(sp, playlist_id)
                    elif choice == "7":
                        # Delete playlist and exit
                        sp.playlist_remove_all_occurrences_of_items(playlist_id, playlist_tracks)
                        sp.user_playlist_unfollow(sp.me()["id"], playlist_id)
                        print("Playlist deleted successfully!")
                        return
                    else:
                        print("Invalid choice. Please choose a valid option.")

                # If the user did not choose to upload, delete the playlist
                if not upload_choice:
                    sp.playlist_remove_all_occurrences_of_items(playlist_id, playlist_tracks)
                    sp.user_playlist_unfollow(sp.me()["id"], playlist_id)
                    print("Playlist deleted successfully!")

                generate_another = input("Would you like to generate another playlist? (Yes/No): ")
                if generate_another.lower() != "yes":
                    break

        elif choice == "4":
            print("\nWelcome to the Spotify Playlist Generation. Need help with how to run the program? You're in the right place!")
            print("It is pretty easy! All you have to do is enter the number next to your desired task!")
            print("For example, if you want to create a playlist through related artists, enter 1.")
            print("If you want to create a playlist full of tracks from a specifc artists, enter 2.")
            print("If you want to create a playlist for a specific genre, enter 3.")
            print("Go ahead and try it out, I promise it won't be that difficult.... \n")
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please choose a valid option.")

# Call the main function
if __name__ == "__main__":
    main()

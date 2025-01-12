"""Functions to use with spotify"""

import csv
import os

import spotipy
from spotipy import SpotifyOAuth

CLIENT_ID = os.getenv("SPOTIFY_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_SECRET")


def load_database(playlist_url):
    """Download the data from a Spotify playlist and save in a csv"""
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri="http://localhost:8888/callback",
            scope="playlist-read-private",
        )
    )
    playlist_id = playlist_url.split("/")[-1].split("?")[0]

    # Prepare a list to store all song data
    songs_data = []

    # Function to get all tracks from the playlist (handle pagination)
    def get_all_tracks(playlist_id):
        results = sp.playlist_items(playlist_id)

        # Loop through each page of results
        while results["next"]:
            for item in results["items"]:
                try:
                    track = item["track"]
                    song_name = track["name"]
                    artist_names = ", ".join(
                        [artist["name"] for artist in track["artists"]]
                    )
                    release_date = track["album"]["release_date"]
                    url = track["external_urls"]["spotify"]
                    songs_data.append([song_name, artist_names, release_date, url])
                except TypeError:
                    print(item)
            # Fetch the next page of tracks
            results = sp.next(results)

        # Don't forget to get the last page of tracks (if it's the first page)
        for item in results["items"]:
            try:
                track = item["track"]
                song_name = track["name"]
                artist_names = ", ".join(
                    [artist["name"] for artist in track["artists"]]
                )
                release_date = track["album"]["release_date"]
                url = track["external_urls"]["spotify"]
                songs_data.append([song_name, artist_names, release_date, url])
            except TypeError:
                print(item)

    # Fetch all tracks from the playlist
    get_all_tracks(playlist_id)

    # Write data to CSV
    with open("spotify_playlist.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Song Name", "Artist(s)", "Release", "Url"])
        writer.writerows(songs_data)

    print(
        f"CSV file 'spotify_playlist.csv' has been created "
        f"successfully with {len(songs_data)} tracks."
    )


def play_song(url):
    """Play the song with the url through the active spotify instance"""
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri="http://localhost:8888/callback",
            scope="user-modify-playback-state user-read-playback-state",
        )
    )
    try:
        track_id = url.split("/")[-1].split("?")[0]
        track_uri = f"spotify:track:{track_id}"
        sp.start_playback(uris=[track_uri])
    except spotipy.exceptions.SpotifyException as e:
        print(f"Error: {e}")

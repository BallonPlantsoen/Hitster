"""Main function to play a terminal based Hitster game"""

import time
from enum import Enum

import pandas as pd

from data import make_the_guess, update_highscores
from spotify import play_song, load_database


class Tile:
    """Tile that represents a card from the Hitster game"""
    def __init__(self, row):
        self.id = row.index.values[0]
        self.name = row["Song Name"].values[0]
        self.artist = row["Artist(s)"].values[0]
        self.year = row["Year"].values[0]
        self.url = row["Url"].values[0]

    def __lt__(self, other):
        if isinstance(other, Tile):
            return self.year < other.year
        return self.year < int(other)

    def __gt__(self, other):
        if isinstance(other, Tile):
            return self.year > other.year
        return self.year > int(other)

    def __ge__(self, other):
        if isinstance(other, Tile):
            return self.year >= other.year
        return self.year >= int(other)

    def __le__(self, other):
        if isinstance(other, Tile):
            return self.year <= other.year
        return self.year <= int(other)


class COLORS(Enum):
    """Enum with some colors to print in the terminal"""
    YEAR = "\033[95m"
    VAR = "\033[94m"
    OKGREEN = "\033[92m"
    INFO = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    def __str__(self):
        return self.value


def load_database_from_csv(url):
    """Load and modify database, create a new one if absent"""
    try:
        df = pd.read_csv("spotify_playlist.csv")
    except FileNotFoundError:
        load_database(url)
        df = pd.read_csv("spotify_playlist.csv")

    def convert_to_year(date):
        """Convert the spotify date to a year"""
        if len(date) == 4 and date.isdigit():
            return int(date)
        return pd.to_datetime(date, errors="coerce").year

    # Apply the conversion function
    df["Year"] = df["Release"].apply(convert_to_year)
    return df


def print_tile(text: str, tile: Tile):
    """Generic print statement for a given tile"""
    print(
        text + f" {COLORS.YEAR}{tile.year}{COLORS.ENDC}. "
        f"It is {COLORS.VAR}{tile.name}{COLORS.ENDC} "
        f"from {COLORS.VAR}{tile.artist}{COLORS.ENDC}."
    )


def start_game(playlist_url):
    """Starts the game"""
    df = load_database_from_csv(playlist_url)

    # Choose a random
    first_tile = Tile(df.sample(n=1))
    df = df.drop([first_tile.id])
    print_tile("You've taken the initial tile with", first_tile)

    current_deck = [first_tile]
    fail_count = 0
    score_count = 0

    while len(current_deck) < 10:
        print(
            f"\n{COLORS.INFO}You've taken a new tile. The song should start playing...{COLORS.ENDC}"
        )

        new_tile = Tile(df.sample(n=1))

        # Run it through Spotify!
        play_song(new_tile.url)

        # Get input for year
        guessed_year = input("\n> Guess the year: ")
        guessed_name = input("\n> Guess the name of the song: ")
        guessed_artist = input("\n> Guess the artist: ")
        result_year, result_name, result_artist = make_the_guess(
            current_deck, new_tile, guessed_year, guessed_name, guessed_artist
        )
        if result_year:
            # Right answer
            print_tile(
                f"\n{COLORS.OKGREEN}[SUCCESS]{COLORS.ENDC} "
                f"You turn the tile over; it is in range! Namely",
                new_tile,
            )
            df = df.drop([new_tile.id])
            current_deck.append(new_tile)
        else:
            # Wrong answer
            fail_count += 1
            print_tile(
                f"\n{COLORS.FAIL}[FAIL ({fail_count})]{COLORS.ENDC} "
                f"You turn the tile over; it is",
                new_tile,
            )

        if result_name and result_artist:
            score_count += 1
            print(
                f"\n{COLORS.OKGREEN}[SUCCESS] You've guessed the name and title right. "
                f"(Score = {score_count}){COLORS.ENDC}"
            )

        print("Your full deck:")
        current_deck.sort()
        for i in current_deck:
            print_tile("- ", i)

    print(
        f"\n{COLORS.INFO}The game is over! You finished getting 10 tiles, with {COLORS.ENDC}"
        f"{COLORS.FAIL}{fail_count} failures {COLORS.ENDC}"
        f"and {COLORS.OKGREEN}{score_count} extra score points{COLORS.ENDC}"
    )
    print("\nUpdating highscores and returning back to main menu.")
    update_highscores()

    time.sleep(2)


if __name__ == "__main__":
    # Specify your playlist link
    PLAYLIST_URL = (
        "https://open.spotify.com/playlist/321iL49aeqqqtKfrQLO91I?si=aeeb907ccaf2490c"
    )
    start_game(PLAYLIST_URL)

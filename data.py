"""Module for calculating guesses, and saving them for later save"""
# pylint: disable=too-few-public-methods, too-many-arguments, too-many-positional-arguments

import json

import Levenshtein

guesses = []


class Guess:
    """Data container for the song guess and answer"""
    def __init__(self, tile, year, name, artist, results):
        self.answer_year = tile.year
        self.answer_name = tile.name
        self.answer_artist = tile.artist
        self.guess_year = year
        self.guess_name = name
        self.guess_artist = artist
        self.results = results

    def to_dict(self) -> dict:
        """Return the guess as a preformatted JSON compliant dict"""
        return {
            "answers": {
                "year": int(self.answer_year),
                "name": self.answer_name,
                "artist": self.answer_artist,
            },
            "guess": {
                "year": int(self.guess_year),
                "name": self.guess_name,
                "artist": self.guess_artist,
            },
            "results": [str(i) for i in self.results]
        }


def make_the_guess(current_deck, tile, year, name="", artist="") -> (bool, bool, bool):
    """Make a guess"""
    try:
        int(year)
    except ValueError:
        year = -1
    min_guess = max((i for i in current_deck if i < tile), default=0)
    max_guess = min((i for i in current_deck if i > tile), default=9999)
    year_result = min_guess <= int(year) <= max_guess

    name_dist = len(name) > 3 and (
        Levenshtein.distance(name, tile.name) < 8 or name.lower() in tile.name.lower()
    )
    artist_dist = len(artist) > 3 and (
        Levenshtein.distance(artist, tile.artist) < 8
        or artist.lower() in tile.artist.lower()
    )

    guesses.append(
        Guess(tile, year, name, artist, (year_result, name_dist, artist_dist))
    )

    return year_result, name_dist, artist_dist


def update_highscores():
    """Store the guesses in a json to possibly do some analysis over"""
    with open("guess_data.json", "w", encoding='utf-8') as fp:
        json.dump([g.to_dict() for g in guesses], fp=fp)

import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# --- Algorithm Recipe (Phase 2) ---
# Genre match:        +2.0  -- strongest categorical signal (identity-level taste)
# Mood match:         +1.0  -- secondary categorical signal (more situational than genre)
# Energy closeness:   up to +2.0, scaled by 1 - |song.energy - target_energy|
#                     -- continuous, so it differentiates the catalog even when
#                        genre/mood don't match (most songs here have a unique
#                        genre and mood, so those two signals are sparse)
# Acousticness fit:   +1.0 if song is on the correct side of the 0.5 threshold
#                     for likes_acoustic -- coarse like/dislike bonus, smallest
#                     weight since it's a threshold check, not a similarity score
# Max possible score: sum of the four constants below (see MAX_POSSIBLE_SCORE)
GENRE_MATCH_POINTS = 2.0
MOOD_MATCH_POINTS = 1.0
ENERGY_MATCH_MAX_POINTS = 2.0
ACOUSTIC_FIT_POINTS = 1.0
MAX_POSSIBLE_SCORE = (
    GENRE_MATCH_POINTS + MOOD_MATCH_POINTS + ENERGY_MATCH_MAX_POINTS + ACOUSTIC_FIT_POINTS
)

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    instrumentalness: float = 0.0
    popularity: float = 0.5

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

def _score_features(
    genre: str,
    mood: str,
    energy: float,
    acousticness: float,
    favorite_genre: str,
    favorite_mood: str,
    target_energy: float,
    likes_acoustic: bool,
) -> Tuple[float, List[str]]:
    """Shared scoring core used by both the functional (dict) and OOP (dataclass) code paths."""
    score = 0.0
    reasons: List[str] = []

    if genre.lower() == favorite_genre.lower():
        score += GENRE_MATCH_POINTS
        reasons.append(f"genre match: {genre} (+{GENRE_MATCH_POINTS:.1f})")

    if mood.lower() == favorite_mood.lower():
        score += MOOD_MATCH_POINTS
        reasons.append(f"mood match: {mood} (+{MOOD_MATCH_POINTS:.1f})")

    energy_gap = abs(energy - target_energy)
    energy_points = max(0.0, 1 - energy_gap) * ENERGY_MATCH_MAX_POINTS
    score += energy_points
    if energy_points > 0:
        reasons.append(
            f"energy ({energy:.2f} vs target {target_energy:.2f}) (+{energy_points:.2f})"
        )

    song_is_acoustic = acousticness >= 0.5
    if song_is_acoustic == likes_acoustic:
        score += ACOUSTIC_FIT_POINTS
        fit_desc = "acoustic" if song_is_acoustic else "non-acoustic"
        reasons.append(f"{fit_desc} fit (+{ACOUSTIC_FIT_POINTS:.1f})")

    return score, reasons


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Score one song against a user's profile using the shared scoring core."""
        return _score_features(
            song.genre,
            song.mood,
            song.energy,
            song.acousticness,
            user.favorite_genre,
            user.favorite_mood,
            user.target_energy,
            user.likes_acoustic,
        )

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs for a user, ranked highest score first."""
        scored = [(song, self._score(user, song)[0]) for song in self.songs]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why a song scored the way it did."""
        score, reasons = self._score(user, song)
        if not reasons:
            return f"Score {score:.2f}: no strong matches, but it's the closest fit available."
        return f"Score {score:.2f}: " + "; ".join(reasons) + "."

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    numeric_fields = (
        "energy", "tempo_bpm", "valence", "danceability",
        "acousticness", "instrumentalness", "popularity",
    )
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["id"] = int(row["id"])
            for field in numeric_fields:
                row[field] = float(row[field])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    return _score_features(
        song["genre"],
        song["mood"],
        song["energy"],
        song["acousticness"],
        user_prefs["favorite_genre"],
        user_prefs["favorite_mood"],
        user_prefs["target_energy"],
        user_prefs["likes_acoustic"],
    )

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons) if reasons else "no strong matches, but the closest fit available"
        scored.append((song, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]

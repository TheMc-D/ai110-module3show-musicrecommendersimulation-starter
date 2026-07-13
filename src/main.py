"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs, MAX_POSSIBLE_SCORE

# Taste profiles: target values for the features Song/UserProfile track.
# Mirrors the UserProfile dataclass fields in recommender.py so both the
# functional (dict) and OOP (dataclass) code paths agree on the same schema.
#
# The first three are distinct "normal" listener profiles. The rest are
# adversarial / edge-case profiles designed to probe the scoring logic for
# unexpected behavior (conflicting signals, out-of-catalog values, boundary
# inputs). See README "Evaluation" section for recorded output and analysis.
USER_PROFILES = {
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.9,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.3,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.95,
        "likes_acoustic": False,
    },
    # --- Adversarial / edge case profiles ---
    "Conflicting: High Energy + Sad Mood": {
        "favorite_genre": "pop",
        "favorite_mood": "melancholic",
        "target_energy": 0.9,
        "likes_acoustic": False,
    },
    "Out-of-Catalog Genre (metal)": {
        "favorite_genre": "metal",
        "favorite_mood": "angry",
        "target_energy": 0.85,
        "likes_acoustic": False,
    },
    "Contradiction: Acoustic-Loving Raver": {
        "favorite_genre": "edm",
        "favorite_mood": "euphoric",
        "target_energy": 0.95,
        "likes_acoustic": True,
    },
    "Boundary: Zero Energy Target": {
        "favorite_genre": "classical",
        "favorite_mood": "melancholic",
        "target_energy": 0.0,
        "likes_acoustic": True,
    },
}


def print_recommendations(profile_name, user_prefs, songs) -> None:
    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("=" * 60)
    print(f"PROFILE: {profile_name}".center(60))
    print("=" * 60)
    print(
        f"genre={user_prefs['favorite_genre']}, "
        f"mood={user_prefs['favorite_mood']}, "
        f"target_energy={user_prefs['target_energy']:.2f}, "
        f"likes_acoustic={user_prefs['likes_acoustic']}\n"
    )

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} by {song['artist']}")
        print(f"   Score: {score:.2f} / {MAX_POSSIBLE_SCORE:.2f}")
        for reason in explanation.split("; "):
            print(f"   - {reason}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")

    for profile_name, user_prefs in USER_PROFILES.items():
        print_recommendations(profile_name, user_prefs, songs)


if __name__ == "__main__":
    main()

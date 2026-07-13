"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Taste profile: target values for the features Song/UserProfile track.
    # Mirrors the UserProfile dataclass fields in recommender.py so both the
    # functional (dict) and OOP (dataclass) code paths agree on the same schema.
    #
    # Known limitation: favorite_genre/favorite_mood are single exact-match
    # values, so any song outside "pop"/"happy" scores 0 on both (5 of 8
    # possible points) and is differentiated only by energy-closeness and
    # acousticness fit. See README Limitations section.
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "likes_acoustic": False,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("=" * 60)
    print("TOP RECOMMENDATIONS".center(60))
    print("=" * 60)
    print(
        f"Profile: {user_prefs['favorite_genre'].title()} / "
        f"{user_prefs['favorite_mood'].title()} "
        f"(target energy {user_prefs['target_energy']:.2f}, "
        f"likes acoustic: {user_prefs['likes_acoustic']})\n"
    )

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} by {song['artist']}")
        print(f"   Score: {score:.2f} / 6.00")
        for reason in explanation.split("; "):
            print(f"   - {reason}")
        print()


if __name__ == "__main__":
    main()

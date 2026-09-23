import numpy as np
import pytest

from story import music

SR = 24000


def _timeline(moods_per_shot, seconds_per_shot=6):
    shots, frame = [], 0
    for moods in moods_per_shot:
        shots.append({"from": frame, "frames": seconds_per_shot * 30, "cast": [{"mood": m} for m in moods]})
        frame += seconds_per_shot * 30
    return {"fps": 30, "episode": "2026-01-01-test", "durationInFrames": frame, "shots": shots}


def _voice(seconds, speaking):
    """A tone during each (start, end) span in `speaking`, silence elsewhere."""
    t = np.arange(int(seconds * SR)) / SR
    v = np.zeros_like(t, dtype=np.float32)
    for a, b in speaking:
        span = (t >= a) & (t < b)
        v[span] = 0.2 * np.sin(2 * np.pi * 220 * t[span])
    return v


def _rms(x):
    return float(np.sqrt(np.mean(x ** 2)))


def test_energy_follows_mood_inserts_inherit_and_the_end_lifts():
    tl = _timeline([["happy"], ["sad", "happy"], [], ["calm"], ["worried"]])
    assert music.shot_energy(tl) == [2.0, 0.0, 0.0, 1.0, 2.0]


def test_none_is_silent():
    tl = _timeline([["calm"]] * 2)
    assert not music.compose(tl, _voice(12, [(1, 3)]), SR, "none").any()


def test_same_episode_same_music():
    tl = _timeline([["calm"], ["happy"]])
    v = _voice(12, [(1, 3), (7, 9)])
    assert np.array_equal(music.compose(tl, v, SR), music.compose(tl, v, SR))


def test_quiet_under_the_voice_and_ducked_while_speaking():
    tl = _timeline([["calm"]] * 3)
    v = _voice(18, [(6, 10)])
    m = music.compose(tl, v, SR)
    assert len(m) == len(v)
    speaking = _rms(m[int(7 * SR):int(9 * SR)])
    between = _rms(m[int(12 * SR):int(14 * SR)])
    assert speaking < between * 0.6                       # ducks while someone speaks
    assert between < _rms(v[int(6 * SR):int(10 * SR)]) * 0.3  # and stays well under the voice


def test_sad_shots_are_sparser_than_happy_ones():
    tl = _timeline([["sad"]] * 3 + [["happy"]] * 3)
    m = music.compose(tl, _voice(36, []) + 1e-3, SR)  # a steady floor: any ducking is uniform
    assert _rms(m[int(5 * SR):int(15 * SR)]) < _rms(m[int(22 * SR):int(32 * SR)])


@pytest.mark.parametrize("t", [0.0, 7.0, 14.0, 21.0])
def test_final_shot_resolves_home(t):
    assert music.chord_at(30.0, final_from=25.0) == music.PROGRESSION[0]
    assert music.chord_at(t, final_from=100.0) in music.PROGRESSION

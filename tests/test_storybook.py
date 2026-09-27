import pytest

from story import storybook


def test_word_search_hides_every_word_and_is_repeatable():
    words = ["HANUMAN", "MANGO", "SUN", "VAYU", "INDRA", "WIND", "CLOUD", "BLESS"]
    grid, placed = storybook.word_search(words, "book-day1")
    assert set(placed) == set(words)
    for w, cells in placed.items():
        assert "".join(grid[r][c] for r, c in cells) == w
    assert storybook.word_search(words, "book-day1") == (grid, placed)


def test_words_too_long_for_the_grid_are_refused(tmp_path):
    (tmp_path / "a.png").write_bytes(b"x")
    (tmp_path / "book.yaml").write_text(
        "schema: story-book/v1\nid: b\ntitle: T\ncover: a.png\n"
        "days: [{day: 1, title: D, cover: a.png, beats: [{image: a.png, text: t}], search: [SUPERCALIFRAGILISTIC],"
        " quiz: [{q: x, options: [a, b], answer: 5}]}]\n")
    with pytest.raises(storybook.BookError) as e:
        storybook.load(tmp_path)
    assert "at most" in str(e.value) and "quiz answer" in str(e.value)


def test_printed_text_gets_curly_quotes():
    assert storybook._smart('"Amma," he said. It\'s \'kind\'.') == "“Amma,” he said. It’s ‘kind’."

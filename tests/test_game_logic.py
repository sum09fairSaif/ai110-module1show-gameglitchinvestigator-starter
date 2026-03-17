import importlib
import sys

import pytest

from logic_utils import check_guess, get_range_for_difficulty


class StopCalled(Exception):
    pass


class RerunCalled(Exception):
    pass


class SessionState(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


class NullContext:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeSidebar:
    def __init__(self, parent):
        self.parent = parent

    def header(self, _label):
        return None

    def selectbox(self, _label, _options, index=0):
        return self.parent.difficulty

    def caption(self, text):
        self.parent.sidebar_captions.append(text)


class FakeStreamlit:
    def __init__(
        self,
        *,
        difficulty="Normal",
        raw_guess="",
        submit=False,
        new_game=False,
        show_hint=True,
        session_state=None,
    ):
        self.difficulty = difficulty
        self.raw_guess = raw_guess
        self.submit_clicked = submit
        self.new_game_clicked = new_game
        self.show_hint_checked = show_hint
        self.session_state = SessionState(session_state or {})
        self.sidebar = FakeSidebar(self)
        self.info_messages = []
        self.warning_messages = []
        self.error_messages = []
        self.success_messages = []
        self.sidebar_captions = []

    def set_page_config(self, **_kwargs):
        return None

    def title(self, _text):
        return None

    def caption(self, _text):
        return None

    def subheader(self, _text):
        return None

    def info(self, text):
        self.info_messages.append(text)

    def expander(self, _label):
        return NullContext()

    def write(self, *_args, **_kwargs):
        return None

    def text_input(self, _label, key=None):
        return self.raw_guess

    def columns(self, count):
        return tuple(NullContext() for _ in range(count))

    def button(self, label):
        if "Submit Guess" in label:
            return self.submit_clicked
        if "New Game" in label:
            return self.new_game_clicked
        return False

    def checkbox(self, _label, value=True):
        return self.show_hint_checked if self.show_hint_checked is not None else value

    def success(self, text):
        self.success_messages.append(text)

    def error(self, text):
        self.error_messages.append(text)

    def warning(self, text):
        self.warning_messages.append(text)

    def balloons(self):
        return None

    def rerun(self):
        raise RerunCalled()

    def stop(self):
        raise StopCalled()

    def divider(self):
        return None


def load_app(monkeypatch, fake_st, randint_values):
    values = iter(randint_values)
    calls = []

    def fake_randint(low, high):
        calls.append((low, high))
        return next(values)

    monkeypatch.setattr("random.randint", fake_randint)
    monkeypatch.setitem(sys.modules, "streamlit", fake_st)
    sys.modules.pop("app", None)
    return calls


def test_winning_guess():
    outcome, _message = check_guess(50, 50)
    assert outcome == "Win"


def test_guess_too_high_returns_lower_hint():
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in message


def test_guess_too_low_returns_higher_hint():
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message


@pytest.mark.parametrize(
    ("difficulty", "expected_range"),
    [("Easy", (1, 20)), ("Normal", (1, 100)), ("Hard", (1, 50))],
)
def test_difficulty_ranges(difficulty, expected_range):
    assert get_range_for_difficulty(difficulty) == expected_range


def test_app_starts_with_zero_attempts_and_shows_selected_range(monkeypatch):
    fake_st = FakeStreamlit(difficulty="Hard")
    load_app(monkeypatch, fake_st, randint_values=[17])

    importlib.import_module("app")

    assert fake_st.session_state.attempts == 0
    assert fake_st.session_state.secret == 17
    assert "Range: 1 to 50" in fake_st.sidebar_captions
    assert "Guess a number between 1 and 50." in fake_st.info_messages[0]
    assert "Attempts left: 5" in fake_st.info_messages[0]


def test_new_game_resets_state_and_uses_difficulty_range(monkeypatch):
    fake_st = FakeStreamlit(
        difficulty="Easy",
        new_game=True,
        session_state={
            "attempts": 4,
            "secret": 99,
            "score": 25,
            "status": "lost",
            "history": [12, 18, "bad input"],
        },
    )
    randint_calls = load_app(monkeypatch, fake_st, randint_values=[7])

    with pytest.raises(RerunCalled):
        importlib.import_module("app")

    assert fake_st.session_state.attempts == 0
    assert fake_st.session_state.secret == 7
    assert fake_st.session_state.score == 0
    assert fake_st.session_state.status == "playing"
    assert fake_st.session_state.history == []
    assert randint_calls == [(1, 20)]


def test_invalid_guess_does_not_consume_attempt(monkeypatch):
    fake_st = FakeStreamlit(
        submit=True,
        raw_guess="",
        session_state={
            "attempts": 0,
            "secret": 10,
            "score": 0,
            "status": "playing",
            "history": [],
        },
    )
    load_app(monkeypatch, fake_st, randint_values=[])

    importlib.import_module("app")

    assert fake_st.session_state.attempts == 0
    assert fake_st.session_state.history == [""]
    assert fake_st.error_messages[-1] == "Enter a guess."


def test_even_attempt_submission_uses_numeric_secret(monkeypatch):
    fake_st = FakeStreamlit(
        submit=True,
        raw_guess="9",
        show_hint=True,
        session_state={
            "attempts": 1,
            "secret": 10,
            "score": 0,
            "status": "playing",
            "history": [],
        },
    )
    load_app(monkeypatch, fake_st, randint_values=[])

    importlib.import_module("app")

    assert fake_st.session_state.attempts == 2
    assert fake_st.session_state.history == [9]
    assert fake_st.warning_messages[-1].endswith("Go HIGHER!")

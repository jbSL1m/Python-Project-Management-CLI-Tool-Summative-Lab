"""Tests for JSON file persistence."""

import pytest

from models import User
from utils import JsonStore


def test_store_saves_and_loads_users(tmp_path):
    """The store should persist user data to a JSON file."""
    store = JsonStore(tmp_path / "nested" / "data.json")
    user = User("Linus", "linus@example.com")

    store.save([user])

    assert store.load()[0].to_dict() == user.to_dict()


def test_store_returns_empty_list_for_missing_file(tmp_path):
    """A first run should work even when no data file exists yet."""
    assert JsonStore(tmp_path / "missing.json").load() == []


def test_store_reports_malformed_json(tmp_path):
    """Malformed data should produce a helpful error instead of a traceback."""
    data_file = tmp_path / "broken.json"
    data_file.write_text("not json", encoding="utf-8")

    with pytest.raises(ValueError, match="Could not read data file"):
        JsonStore(data_file).load()
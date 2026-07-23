from main import parse_handle_list


def test_parse_handle_list_returns_none_for_empty_value():
    assert parse_handle_list("") is None
    assert parse_handle_list(" , ") is None


def test_parse_handle_list_returns_none_for_wildcard():
    assert parse_handle_list("*") is None
    assert parse_handle_list("@admin,*") is None


def test_parse_handle_list_strips_empty_items_and_spaces():
    assert parse_handle_list(" @one, ,@two ") == ["@one", "@two"]

from bot.telegram.utils import min_char_diff_for_buffering


def test_min_char_diff_for_buffering_private_chat_thresholds():
    assert min_char_diff_for_buffering("x" * 10, is_group_chat=False) == 15
    assert min_char_diff_for_buffering("x" * 51, is_group_chat=False) == 25
    assert min_char_diff_for_buffering("x" * 201, is_group_chat=False) == 45
    assert min_char_diff_for_buffering("x" * 1001, is_group_chat=False) == 90


def test_min_char_diff_for_buffering_group_chat_thresholds():
    assert min_char_diff_for_buffering("x" * 10, is_group_chat=True) == 50
    assert min_char_diff_for_buffering("x" * 121, is_group_chat=True) == 90
    assert min_char_diff_for_buffering("x" * 201, is_group_chat=True) == 120
    assert min_char_diff_for_buffering("x" * 1001, is_group_chat=True) == 180

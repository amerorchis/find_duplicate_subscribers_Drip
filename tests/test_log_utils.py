"""Tests for log masking: full subscriber addresses must never reach the logs."""

import logging

from find_dupes import find_duplicates
from log_utils import mask_email


class TestMaskEmail:
    """Masking keeps the first character and the domain only."""

    def test_masks_local_part(self):
        assert mask_email('john.smith@gmail.com') == 'j***@gmail.com'

    def test_strips_whitespace(self):
        assert mask_email('  john@example.com ') == 'j***@example.com'

    def test_multiple_at_signs_keep_last_domain(self):
        assert mask_email('a@b@c.com') == 'a***@c.com'

    def test_no_at_sign(self):
        assert mask_email('not-an-email') == 'n***'

    def test_empty(self):
        assert mask_email('') == '***'


def test_unparseable_emails_are_logged_masked(caplog):
    with caplog.at_level(logging.INFO):
        find_duplicates(['secret.person@@example.com', 'ok@example.com'])
    assert 's***@example.com' in caplog.text
    assert 'secret.person' not in caplog.text
    assert 'Skipped 1 unparseable email(s)' in caplog.text

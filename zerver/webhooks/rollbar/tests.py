# -*- coding: utf-8 -*-
from typing import Text

from zerver.lib.test_classes import WebhookTestCase

class RollbarHookTests(WebhookTestCase):
    STREAM_NAME = 'rollbar'
    URL_TEMPLATE = "/api/v1/external/rollbar?&api_key={api_key}"
    FIXTURE_DIR_NAME = 'rollbar'

    def test_message(self) -> None:
        expected_subject = u"Rollbar"
        expected_message = u"This is a test message from Rollbar. If you got this, it works!"

        self.send_and_test_stream_message('test', expected_subject, expected_message,
                                          content_type="application/x-www-form-urlencoded")

    def test_new_item(self) -> None:
        expected_subject = u"Rollbar"
        expected_message = u"""[NewProject] production - New Error: An Error
https://rollbar.com/kiy4h/NewProject/items/7/"""

        self.send_and_test_stream_message('new_item', expected_subject, expected_message,
                                          content_type="application/x-www-form-urlencoded")

    def test_item_resolved(self) -> None:
        expected_subject = u"Rollbar"
        expected_message = u"""[NewProject] production - Resolved by Kiy4h: All set.
https://rollbar.com/kiy4h/NewProject/items/3/"""

        self.send_and_test_stream_message('resolved_item', expected_subject, expected_message,
                                          content_type="application/x-www-form-urlencoded")

    def test_reopen_item(self) -> None:
        expected_subject = u"Rollbar"
        expected_message = u"""[NewProject] production - Reopened by Kiy4h: All set.
https://rollbar.com/kiy4h/NewProject/items/3/"""

        self.send_and_test_stream_message('reopen_item', expected_subject, expected_message,
                                          content_type="application/x-www-form-urlencoded")

    def test_reactivated_item(self) -> None:
        expected_subject = u"Rollbar"
        expected_message = u"""[NewProject] production - Reactivated Error: All set.
https://rollbar.com/kiy4h/NewProject/items/3/"""

        self.send_and_test_stream_message('reactivated_item', expected_subject, expected_message,
                                          content_type="application/x-www-form-urlencoded")

    def test_high_occurence_rate(self) -> None:
        expected_subject = u"Rollbar"
        expected_message = u"""[NewProject] production - 10 occurrences in 5 minutes: All set.
https://rollbar.com/kiy4h/NewProject/items/3/"""

        self.send_and_test_stream_message('high_occurence_rate', expected_subject, expected_message,
                                          content_type="application/x-www-form-urlencoded")

    def test_exp_repeat_item(self) -> None:
        expected_subject = u"Rollbar"
        expected_message = u"""[NewProject] production - 10th Error: An Error
https://rollbar.com/kiy4h/NewProject/items/7/"""

        self.send_and_test_stream_message('event_occurred_10_exp_n_items', expected_subject, expected_message,
                                          content_type="application/x-www-form-urlencoded")

    def test_occurrence(self) -> None:
        expected_subject = u"Rollbar"
        expected_message = u"""[NewProject] production - new again again (Error)
https://rollbar.com/kiy4h/NewProject/items/10/occurrences/35726608174/"""

        self.send_and_test_stream_message('every_occurrence', expected_subject, expected_message,
                                          content_type="application/x-www-form-urlencoded")

    def get_body(self, fixture_name: Text) -> Text:
        return self.fixture_data("rollbar", fixture_name, file_type="json")

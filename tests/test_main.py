import unittest
from main import get_last_id_from_tweets, get_link_messages, build_tweets_list
from unittest.mock import Mock
import datetime


class MainTestCase(unittest.TestCase):
    def test_get_last_id_from_tweets(self):
        sample = [
            "hey folks", "Links for the week (Last Message ID: 89569)", "here is a link: http://google.com", "here is another one http://google.com"]
        self.assertEqual(89569, get_last_id_from_tweets(sample))

    def test_get_last_id_from_tweets_null_case(self):
        sample = ["hey folks", "that's all folks"]
        self.assertEqual(None, get_last_id_from_tweets(sample))

    def test_get_messages(self):
        mocked_message1 = Mock()
        mocked_message1.message = "no links"
        mocked_message2 = Mock()
        mocked_message2.message = "here is a link: http://google.com"
        mocked_message3 = Mock()
        mocked_message3.message = "this does not count: https://t.me/datasciencepython/47854"

        mocked_client = Mock()

        async def mocked_get_messages(group, min_id, limit, reverse):
            return [mocked_message1, mocked_message2, mocked_message3]
        mocked_client.get_messages = mocked_get_messages

        result = get_link_messages(
            mocked_client, 0)
        expected = [mocked_message2]
        self.assertEqual(expected, result)

    def test_build_tweets_list(self):
        msg1 = Mock()
        msg1.message = "muito legal!\nhttp://www.pudim.com.br\nné?"
        msg2 = Mock()
        msg2.message = "here is a link:http://google.com but with a super super super super super super super super super super super super super super super super super super super super super super super super super super long text"
        msg2.id = 1001
        msg2.date = datetime.datetime(2019, 4, 3, 20, 43, 4)

        result = build_tweets_list([msg1, msg2])
        expected = [
            "Data Science Links 03/04 (Last Message ID: 1001)",
            "muito legal!\nhttp://www.pudim.com.br\nné?",
            "here is a link:http://google.com but with a super super super super super super super super super super super super super super super super super super super super super super super super super super ..."
        ]
        self.assertEqual(expected, result)

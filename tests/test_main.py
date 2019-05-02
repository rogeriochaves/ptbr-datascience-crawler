import unittest
from main import get_last_id, get_link_messages, build_links_list, get_article_details
from unittest.mock import Mock
import datetime


class MainTestCase(unittest.TestCase):
    def test_get_last_id(self):
        sample = "04/04/2019 17:45\nLast Message ID: 456\n\n- foo\n- bar\nLast Message ID: 123"
        self.assertEqual(456, get_last_id(sample))

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

    def test_build_links_list(self):
        msg1 = Mock()
        msg1.message = "muito legal!\nhttp://www.pudim.com.br\nné?"
        msg2 = Mock()
        msg2.message = "here is a link:http://google.com"
        msg2.id = 1001
        msg2.date = datetime.datetime(2019, 4, 3, 20, 43, 4)

        result = build_links_list([msg1, msg2])
        expected = """### 03/04/2019 20:43
Last Message ID: 1001

muito legal!

né?

| [Pudim](http://www.pudim.com.br) | [<img src="http://www.pudim.com.br/pudim.jpg" width="300">](http://www.pudim.com.br) |
| -- | -- |

here is a link:

| [Google](http://google.com) | [<img src="" width="300">](http://google.com) |
| -- | -- |"""
        self.assertEqual(expected, result)

    def test_get_article_details(self):
        msg1 = Mock()
        msg1.message = "muito legal!\nhttp://www.pudim.com.br\nné?"

        result = get_article_details(msg1)
        self.assertEqual({"title": "Pudim",
                          "top_image": "http://www.pudim.com.br/pudim.jpg",
                          "url": "http://www.pudim.com.br",
                          "message": "muito legal!\n\nné?"}, result)

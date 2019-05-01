from github import Github, InputFileContent
from telethon import TelegramClient, events, sync
import re
import os
import base64

# Get your own api_id and api_hash from https://my.telegram.org, under API Development.
api_id = os.environ['API_ID']
api_hash = os.environ['API_HASH']
# Get the github token from https://github.com/settings/tokens
github_token = os.environ['GITHUB_TOKEN']

if os.environ['SESSION_DB']:
    with open("session_name.session", "wb") as file:
        file.write(base64.b64decode(os.environ['SESSION_DB']))


def get_gist():
    g = Github(github_token)
    return g.get_gist("bc1469d0a8ed0de01369aa34be2bad76")


def get_last_id(content):
    matches = re.search(r'Last Message ID: (.*)', content)
    return int(matches[1])


def get_link_messages(client, offset):
    messages = client.get_messages(
        'datasciencepython', min_id=offset, limit=300, reverse=True)
    messages_with_links = filter(lambda m:
                                 m.message and
                                 re.match(r'.*https?://.*', m.message) and
                                 not "t.me/datasciencepython" in m.message, messages)

    return list(messages_with_links)


def build_links_list(messages):
    timestamp = messages[-1].date.strftime('%d/%m/%Y %H:%M')
    last_id = messages[-1].id
    messages_list = "\n".join(
        ["- %s" % re.sub(r'\n', '\n  ', m.message) for m in messages])
    return "### %s\nLast Message ID: %d\n\n%s" % (timestamp, last_id, messages_list)


if __name__ == "__main__":
    client = TelegramClient('session_name', api_id, api_hash)
    client.start()
    print("Connected to Telegram!")

    gist = get_gist()
    file = gist.files['links.md']
    content = file.content
    last_id = get_last_id(content)
    print("Getting messages after", last_id)

    messages = get_link_messages(client, last_id)
    print(len(messages), "links found")
    if len(messages) == 0:
        print("No links to save")
        exit(0)

    new_content = build_links_list(messages)
    new_file = InputFileContent(new_content + "\n\n" + content)

    print("Saving gist")
    gist.edit(files={'links.md': new_file})

    print("Done! https://gist.github.com/rogeriochaves/bc1469d0a8ed0de01369aa34be2bad76")

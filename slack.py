import os
import slack


def set_slack_status(status):

    if os.path.exists('slack-token.txt'):
        slack_token = open('slack-token.txt', 'rb').read()
    else:
        print('No token set for slack')

    client = slack.WebClient(token=slack_token)

    profile = client.users_profile_get()
    print(profile)
    # response = client.chat_postMessage(
    #     channel='#random',
    #     text="Hello world!")
    # assert response["ok"]
    # assert response["message"]["text"] == "Hello world!"


if __name__ == '__main__':
    set_slack_status("testing")

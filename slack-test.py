import os
import slack


def set_slack_status(status):

    slack_token = None
    if os.path.exists('slack-token.txt'):
        slack_token = str(open('slack-token.txt', 'r').read())
    else:
        print('No token set for slack')

    slack_user = None
    if os.path.exists('slack-user.txt'):
        slack_user = str(open('slack-user.txt', 'r').read())
    else:
        print('No user set for slack')

    print("fetching data for user", slack_user)

    client = slack.WebClient(token=slack_token)

    profile = client.users_profile_get(user=slack_user)
    print(profile.get('profile').get('status_text'))

    client.users_profile_set(user=slack_user, name='status_text', value='Testing stuff')


if __name__ == '__main__':
    set_slack_status("testing")

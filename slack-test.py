import os
import slack


slack_token = None
if os.path.exists('slack-token.txt'):
    slack_token = str(open('slack-token.txt', 'r').read()).strip()
else:
    print('No token set for slack')

slack_user = None
if os.path.exists('slack-user.txt'):
    slack_user = str(open('slack-user.txt', 'r').read()).strip()
else:
    print('No user set for slack')


slack_client = slack.WebClient(token=slack_token)

print("users", slack_client.users_list())


def get_slack_status():
    print("fetching data for user", slack_user)

    profile = slack_client.users_profile_get(user=slack_user)
    print(profile.get('profile').get('status_text'))


def set_slack_status(status):
    print("setting status for user", slack_user, status)
    slack_client.users_profile_set(user=slack_user, name='status_text', value='Testing stuff')


if __name__ == '__main__':
    get_slack_status()

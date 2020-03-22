from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def get_calendar_items(calendarId):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(calendarId + '-token.pickle'):
        with open(calendarId + '-token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_console()
        # Save the credentials for the next run
        with open(calendarId + '-token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    eventList = []

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date')).replace("Z", "+00:00")
        end = event['end'].get('dateTime', event['end'].get('date')).replace("Z", "+00:00")
        duration = int((datetime.datetime.fromisoformat(end) - datetime.datetime.fromisoformat(start)).seconds / 60)
        attendees = []
        for person in event.get('attendees', []):
            attendees.append({'name': person.get('displayName', person.get('email')), 'response': person.get('responseStatus')})
        # print(start, event['organizer'].get('email'), event['summary'], event['attendees'])
        eventData = {'summary': event['summary'], 'start_time': start, 'end_time': end, 'duration': duration, 'organizer': event['organizer'].get('email'), 'attendees': attendees}
        eventList.append(eventData)
        # print(eventData)

    return eventList


def get_all_calendar_items():
    eventList = get_calendar_items("vestd") + get_calendar_items("personal")
    eventList = sorted(eventList, key=lambda event: event.get('start_time'))
    return eventList


if __name__ == '__main__':
    today = datetime.datetime.now()
    tomorrow = today + datetime.timedelta(days=1)
    eventList = get_all_calendar_items()
    for event in eventList:
        start_time = datetime.datetime.fromisoformat(event.get('start_time'))
        if start_time.date() == today.date():
            print(start_time.strftime("%A %d %B %Y %H:%M"), event.get('duration'), event.get('summary'))
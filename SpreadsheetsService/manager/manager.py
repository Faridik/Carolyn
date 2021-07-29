import os.path
from googleapiclient.discovery import _MEDIA_SIZE_BIT_SHIFTS, build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from models.student import Student
from models.group import Group

class Manager:
    """Позволяет выполнять операции с Google таблицами."""

    def __init__(self, spreadsheet_id: str='1GKfmLwDVGjcpXFQAUyxM4RMQ5Nx6HAZ5VWenz2z--d0',
                    scopes: list=['https://www.googleapis.com/auth/spreadsheets.readonly']):
        
        self.spreadsheet_id = spreadsheet_id

        creds = None

        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secret.json', scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        service = build('sheets', 'v4', credentials=creds)
        self.sheet = service.spreadsheets()


    def get_group(self, group_id: int) -> Group:
        """Получить группу со студентами."""

        GROUPS = 2
        STUDENT_NUMBERS = 0
        STUDENT_NAMES = 1

        result = self.sheet.values().get(spreadsheetId=self.spreadsheet_id,
                                range='Студенты!A2:Z').execute()
        values = result.get('values', [])

        group = Group(group_id)

        f = lambda row: group_id == int(row[GROUPS])
        for row in filter(f, values):
            group.add_student(Student(int(row[STUDENT_NUMBERS]), row[STUDENT_NAMES]))

        return group
        

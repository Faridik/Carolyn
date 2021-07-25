from __future__ import print_function
import os.path
from googleapiclient.discovery import _MEDIA_SIZE_BIT_SHIFTS, build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# ID таблицы и range (страница + интересующие ячейки).
# Эти данные скрывать не нужно, так как таблица не доступна другим пользователям
SAMPLE_SPREADSHEET_ID = '1peseFgZ-Or5N711ja4po05dyM6gzPzFTtvQWk3jR2eM'
SAMPLE_RANGE_NAME = 'Успеваемость!A1:AAA'

STUDENT_NAME = 'Бронвальд Леонид'

def main():

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Создание запроса и получение значений таблицы
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    # Генерация ответа на запрос
    message = f'Рада тебя видеть, {STUDENT_NAME}! '

    # Нахождение номера студента со смещением для поиска в таблице
    # (можно пользоваться номером студента, а не его именем, но список студентов может меняться
    # из-за отчислений других студентов)
    studentNumber = -1
    for row, value in enumerate(values):
        if STUDENT_NAME in value:
            studentNumber = row
            break
    
    # Ошибка поиска
    if studentNumber == -1:
        message += 'К сожалению, не удалось найти тебя в таблице успеваемости. За помощью обратись к Фариду.'
        print(message)
        return message

    message += 'На данный момент твои результаты выглядят следующим образом:\n\n'

    # Поиск типов заданий и генерация сообщений по этим заданиям
    isWritten = True # Переменная из-за нулей в пустой сумме
    for col, value in enumerate(values[0]):
        
        # Обработка ИДЗ и ДЗ в таблице
        if 'ДЗ' in value:
            message += f'\t{value}\n'
            for colTask, numberTask in enumerate(values[1][col:]):
                if numberTask:
                    message += f'{numberTask}. '
                    if values[studentNumber][col + colTask] == '1':
                        message += 'Засчитан.\n'
                    else:
                        message += 'Не засчитан.\n'
                else:
                    break

        # Обработка КР в таблице
        elif 'КР' in value:
            message += f'\t{value}\n'
            if values[studentNumber][col]:
                for colTask, numberTask in enumerate(values[1][col:]):
                    if numberTask:
                        message += f'{numberTask}. {values[studentNumber][col + colTask]}\n'
                    else:
                        break
            else:
                message += 'КР не проверена или не написана.\n\n'
                isWritten = False

        # Обработка штрафов
        elif 'Ш' in value:
            if values[studentNumber][col] == '0':
                message += 'Штраф по этой работе отсутствует\n\n'
            else:
                message += f'Штраф по этой работе составляет {values[studentNumber][col]}\n\n'
        
        # Обработка суммы в таблице (после кр и после дз)
        elif 'S' in value:
            if isWritten:
                message += f'Сумма работы составляет: {values[studentNumber][col]}\n\n'
            isWritten = True

        # Обработка итоговой оценки в таблице (пример по матану, с оценкой и без допуска)
        elif 'Итого' in value:
            if values[studentNumber][col]:
                message += f'Итоговая оценка составляет: {values[studentNumber][col]}\n'
            else:
                message += 'Итоговая оценка ещё не выставлена.\n'

        # Обработка количества баллов
        elif 'Баллы' in value:
            message += f'Баллов за семестр набрано: {values[studentNumber][col]}\n\n'

    # Проверка
    print(message)

    return message
    

if __name__ == '__main__':
    main()
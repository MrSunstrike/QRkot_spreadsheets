import copy
from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings
from app.models.charity_project import CharityProject

SPREADSHEET_BODY = {
    "properties": {
        "title": "Отчет от определенной даты",
        "locale": "ru_RU"
    },
    "sheets": [
        {
            "properties": {
                "sheetType": "GRID",
                "sheetId": 0,
                "title": "Лист1",
                "gridProperties": {
                    "rowCount": 100,
                    "columnCount": 11
                }
            }
        }
    ]
}
TABLE_VALUES = [
    ["Отчет от", "дата"],
    ["Топ проектов по скорости закрытия"],
    ["Название проекта", "Время сбора", "Описание"]
]


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    now_date_time = datetime.now().strftime(settings.date_format)

    service = await wrapper_services.discover("sheets", "v4")

    spreadsheet_body = {
        "properties": {
            "title": f"Отчёт на {now_date_time}",
            "locale": "ru_RU"
        },
        "sheets": [
            {
                "properties": {
                    "sheetType": "GRID",
                    "sheetId": 0,
                    "title": "Лист1",
                    "gridProperties": {
                        "rowCount": 100,
                        "columnCount": 11
                    }
                }
            }
        ]
    }

    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )

    spreadsheet_id = response["spreadsheetId"]

    return spreadsheet_id


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = {
        "type": "user",
        "role": "writer",
        "emailAddress": settings.email
    }
    service = await wrapper_services.discover("drive", "v3")

    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheet_id: str,
        projects: list[CharityProject],
        wrapper_services: Aiogoogle
) -> None:
    now_date_time = datetime.now().strftime(settings.date_format)

    service = await wrapper_services.discover("sheets", "v4")

    table_values = copy.deepcopy(TABLE_VALUES)
    table_values[0] = ["Отчет от", now_date_time]

    for project in projects:
        project_row = [
            str(project.name),
            str(project.create_date - project.close_date),
            str(project.description)
        ]
        table_values.append(project_row)

    update_body = {
        "majorDimension": "ROWS",
        "values": table_values
    }

    rows = len(table_values)
    columns = max(map(len, table_values))

    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f"R1C1:R{rows}C{columns}",
            valueInputOption="USER_ENTERED",
            json=update_body
        )
    )

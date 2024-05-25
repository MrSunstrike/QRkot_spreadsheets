from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject


async def check_project_exists(project_id: int, session: AsyncSession):
    project = await charity_project_crud.get(project_id, session)

    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Нет такого проекта!'
        )

    return project


def check_project_does_not_have_investors(
    project: CharityProject,
):

    if project.invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=('Нельзя удалить проект, в который уже были инвестированы'
                    'средства, его можно только закрыть.')
        )


def check_full_amount_ge_invested_amount(
    project: CharityProject,
    updated_amount: int
):

    if project.invested_amount > updated_amount:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Нельзя установить требуемую сумму меньше уже вложенной!'
        )


async def check_project_name_is_unique(
    new_project_name: str,
    session: AsyncSession
):
    duplicate = await charity_project_crud.get_project_by_name(
        new_project_name,
        session
    )

    if duplicate is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Такое имя уже существует, выберите другое!'
        )


def check_project_is_closed(
    project: CharityProject,
):

    if project.close_date is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!'
        )

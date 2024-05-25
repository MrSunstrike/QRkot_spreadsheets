from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_full_amount_ge_invested_amount,
                                check_project_does_not_have_investors,
                                check_project_exists, check_project_is_closed,
                                check_project_name_is_unique)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import ProjectCreate, ProjectDB, ProjectUpdate
from app.services.investment_processor import project_workflow

router = APIRouter()


@router.get('/', response_model=list[ProjectDB])
async def get_all_projects(
    session: AsyncSession = Depends(get_async_session),
):
    """Возвращает список всех проектов."""

    projects = await charity_project_crud.get_multi(session)

    return projects


@router.post(
    '/',
    response_model=ProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def create_new_charity_project(
    json_in: ProjectCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров.
    Создаёт благотворительный проект."""

    new_name = json_in.name
    await check_project_name_is_unique(new_name, session)

    new_project = await charity_project_crud.create(json_in, session)
    await project_workflow(new_project, session)

    return new_project


@router.delete(
    '/{project_id}',
    response_model=ProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def delete_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров.
    Удаляет проект. Нельзя удалить проект, в который уже были инвестированы
    средства, его можно только закрыть."""

    project = await check_project_exists(project_id, session)
    check_project_does_not_have_investors(project)
    removed_project = await charity_project_crud.remove(project, session)

    return removed_project


@router.patch(
    '/{project_id}',
    response_model=ProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def update_project(
    project_id: int,
    json_in: ProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров.
    Закрытый проект нельзя редактировать; нельзя установить требуемую сумму
    меньше уже вложенной."""

    project_to_update = await check_project_exists(project_id, session)
    check_project_is_closed(project_to_update)

    if json_in.name:
        new_name = json_in.name
        await check_project_name_is_unique(new_name, session)

    if json_in.full_amount is not None:
        new_amount = json_in.full_amount
        check_full_amount_ge_invested_amount(project_to_update, new_amount)

    updated_project = await charity_project_crud.update(
        project_to_update,
        json_in,
        session,
    )

    return updated_project

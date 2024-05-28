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
from app.services.investment_processor import project_investing

router = APIRouter()


@router.get('/', response_model=list[ProjectDB])
async def get_all_projects(
    session: AsyncSession = Depends(get_async_session),
) -> list[ProjectDB]:
    """
    Возвращает список всех проектов.
    """
    projects = await charity_project_crud.get_multi(session)

    return projects


@router.post(
    '/',
    response_model=ProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def create_new_charity_project(
    data: ProjectCreate,
    session: AsyncSession = Depends(get_async_session),
) -> ProjectDB:
    """
    Только для суперюзеров. Создаёт благотворительный проект.
    """
    new_name = data.name
    await check_project_name_is_unique(new_name, session)

    new_project = await charity_project_crud.create(
        obj_in=data,
        session=session,
        commit=False
    )

    donations = await project_investing(
        session=session,
        project=new_project
    )

    session.add(new_project)
    session.add_all(donations)

    await session.commit()
    await session.refresh(new_project)

    return new_project


@router.delete(
    '/{project_id}',
    response_model=ProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def delete_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> ProjectDB:
    """
    Только для суперюзеров. Удаляет проект. Нельзя удалить проект, в который
    уже были инвестированы средства, его можно только закрыть.
    """
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
    data: ProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> ProjectDB:
    """
    Только для суперюзеров. Закрытый проект нельзя редактировать; нельзя
    установить требуемую сумму меньше уже вложенной.
    """
    project_to_update = await check_project_exists(project_id, session)
    check_project_is_closed(project_to_update)

    if data.name:
        new_name = data.name
        await check_project_name_is_unique(new_name, session)

    if data.full_amount is not None:
        new_amount = data.full_amount
        check_full_amount_ge_invested_amount(project_to_update, new_amount)

    updated_project = await charity_project_crud.update(
        project_to_update,
        data,
        session,
    )

    return updated_project

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import (DonationCreate, DonationDB,
                                  DonationProcessorDB)
from app.services.investment_processor import donation_investing

router = APIRouter()


@router.post('/', response_model=DonationDB, response_model_exclude_none=True)
async def create_donation(
    donation: DonationCreate,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
) -> DonationCreate:
    """
    Сделать пожертвование.
    """
    new_donation = await donation_crud.create(
        obj_in=donation,
        session=session,
        user=user,
        commit=False
    )

    projects = await donation_investing(session=session, donation=new_donation)

    session.add(new_donation)
    session.add_all(projects)

    await session.commit()
    await session.refresh(new_donation)

    return new_donation


@router.get(
    '/',
    response_model=list[DonationProcessorDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session)
) -> list[DonationProcessorDB]:
    """
    Только для суперюзеров. Возвращает список всех пожертвований.
    """
    donations = await donation_crud.get_multi(session)

    return donations


@router.get(
    '/my',
    response_model=list[DonationDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_user)],
)
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
) -> list[DonationProcessorDB]:
    """
    Вернуть список пожертвований пользователя, выполняющего запрос.
    """
    my_donations = await donation_crud.get_my_donations(user, session)

    return my_donations

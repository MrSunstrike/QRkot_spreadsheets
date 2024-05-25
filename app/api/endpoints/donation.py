from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import DonationBase, DonationCreate, DonationDB
from app.services.investment_processor import donation_workflow

router = APIRouter()


@router.post('/', response_model=DonationCreate)
async def create_donation(
    donation: DonationBase,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Сделать пожертвование."""

    new_donation = await donation_crud.create(donation, session, user)
    await donation_workflow(new_donation, session)

    return new_donation


@router.get(
    '/',
    response_model=list[DonationDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров.
    Возвращает список всех пожертвований."""

    donations = await donation_crud.get_multi(session)

    return donations


@router.get(
    '/my',
    response_model=list[DonationCreate],
    response_model_exclude_none=True,
    dependencies=[Depends(current_user)],
)
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Вернуть список пожертвований пользователя, выполняющего запрос."""

    my_donations = await donation_crud.get_my_donations(user, session)

    return my_donations

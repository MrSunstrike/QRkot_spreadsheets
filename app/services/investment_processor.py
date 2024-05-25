from datetime import datetime
from typing import Union

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.models import CharityProject, Donation


async def find_project_for_investment(
        session: AsyncSession = Depends(get_async_session)
):
    project_for_investment = await session.execute(
        select(CharityProject).where(
            CharityProject.fully_invested == 0
        )
    )
    return project_for_investment.scalars().all()


async def find_donation_to_invest(
        session: AsyncSession = Depends(get_async_session)
):
    donation_to_invest = await session.execute(
        select(Donation).where(
            Donation.fully_invested == 0
        )
    )
    return donation_to_invest.scalars().all()


async def close_fully_invested_object(obj: Union[CharityProject, Donation]):
    obj.invested_amount = obj.full_amount
    obj.fully_invested = True
    obj.close_date = datetime.now()


async def processor(project: CharityProject, donation: Donation):
    investment_balance = project.full_amount - project.invested_amount
    donation_balance = donation.full_amount - donation.invested_amount
    if investment_balance > donation_balance:
        project.invested_amount += donation_balance
        await close_fully_invested_object(donation)
    if donation_balance > investment_balance:
        donation.invested_amount += investment_balance
        await close_fully_invested_object(project)
    if investment_balance == donation_balance:
        await close_fully_invested_object(project)
        await close_fully_invested_object(donation)
    return project, donation


async def project_workflow(
        project: CharityProject,
        session: AsyncSession = Depends(get_async_session)
):
    donations_coroutine = await find_donation_to_invest(session)

    for donation in donations_coroutine:
        await processor(project, donation)
        session.add(project)
        session.add(donation)

    await session.commit()
    await session.refresh(project)

    return project


async def donation_workflow(
        donation: Donation, session: AsyncSession = Depends(get_async_session)
):
    projects_coroutine = await find_project_for_investment(session)

    for project in projects_coroutine:
        await processor(project, donation)
        session.add(project)
        session.add(donation)

    await session.commit()
    await session.refresh(donation)

    return donation

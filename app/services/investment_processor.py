from datetime import datetime
from typing import List, Union

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.schemas.charity_project import ProjectDB
from app.schemas.donation import DonationProcessorDB


async def fully_invested(obj: Union[ProjectDB, DonationProcessorDB]) -> None:
    obj.fully_invested = True
    obj.invested_amount = obj.full_amount
    obj.close_date = datetime.now()


async def processor(donation: DonationProcessorDB, project: ProjectDB) -> bool:
    if donation.fully_invested or project.fully_invested:
        return True

    donation_to_distribute = donation.full_amount - (
        donation.invested_amount or 0
    )

    project_to_close = project.full_amount - (
        project.invested_amount or 0
    )

    if project_to_close < donation_to_distribute:
        donation.invested_amount += project_to_close
        await fully_invested(project)

    elif project_to_close > donation_to_distribute:
        project.invested_amount += donation_to_distribute
        await fully_invested(donation)

    else:
        await fully_invested(project)
        await fully_invested(donation)


async def donation_investing(
    session: AsyncSession,
    donation: DonationProcessorDB
) -> List[ProjectDB]:
    projects = await charity_project_crud.get_items_to_process(session)
    result = list()

    for project in projects:
        if await processor(donation=donation, project=project):
            break

        result.append(project)

    return result


async def project_investing(
    session: AsyncSession,
    project: ProjectDB
) -> List[DonationProcessorDB]:
    donations = await donation_crud.get_items_to_process(session=session)
    result = list()

    for donation in donations:
        if await processor(donation=donation, project=project):
            break

        result.append(donation)

    return result

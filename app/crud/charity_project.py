from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_crud import CRUDBase
from app.models.charity_project import CharityProject


class ProjectCRUD(CRUDBase):

    @staticmethod
    async def get_project_by_name(
        project_name: str,
        session: AsyncSession,
    ) -> None:

        project = await session.execute(
            select(CharityProject).where(
                CharityProject.name == project_name
            )
        )

        return project.scalars().first()

    @staticmethod
    async def get_projects_by_completion_rate(session: AsyncSession):

        closed_projects = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested.is_(True)
            ).order_by(CharityProject.close_date - CharityProject.create_date)
        )

        return closed_projects.scalars().all()


charity_project_crud = ProjectCRUD(CharityProject)

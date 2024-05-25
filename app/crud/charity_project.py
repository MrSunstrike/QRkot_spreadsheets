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


charity_project_crud = ProjectCRUD(CharityProject)

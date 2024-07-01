from fastapi import status, HTTPException
from sqlalchemy.sql import func
from typing import Optional
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.orm import Session

import db.tables as tables
from models.experiments import ExperimentCreate

class ExperimentsService:
    def __init__(self, session: Session):
        self.session = session

    async def get_file(self, id) -> Optional[list]:
        result = await self.session.execute(
            select(tables.Experiments.link).
            filter_by(id=id)
        )
        return result.scalars().all()

    async def get(self, test_type: str = None) -> Optional[tables.Experiments]:
        if test_type:
            result = await self.session.execute(
                select(tables.Experiments).
                filter_by(test_type=test_type)
            )
        else:
            result = await self.session.execute(
                select(tables.Experiments)
            )

        experiments = result.scalars().all()

        if not experiments:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Not found',
            )

        return experiments

    async def get_test_types(self) -> Optional[list]:
        result = await self.session.execute(
            select(tables.Experiments.test_type).distinct()
        )
        return result.scalars().all()

    async def create(self, data: ExperimentCreate, filename: str) -> tables.Experiments:
        id = await self.session.execute(func.nextval('experiments_id_seq'))
        id = id.scalar()

        experiment = tables.Experiments(
            id=id,
            link=f"plotter/{id}_{filename}",
            test_type=data.test_type,
            laboratory_number=data.laboratory_number,
            object_number=data.object_number,
            description=data.description
        )
        self.session.add(experiment)
        await self.session.commit()

        return experiment

    async def delete(self, id: int):
        q = delete(tables.Experiments).where(tables.Experiments.id == id)
        q.execution_options(synchronize_session='fetch')
        await self.session.execute(q)
        await self.session.commit()



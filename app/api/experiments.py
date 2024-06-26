from fastapi import APIRouter, Depends, Response, status, UploadFile, HTTPException
from typing import List

from services.depends import get_experiments_service, get_s3_service
from services.experiments import ExperimentsService
from services.auth import get_current_username
from services.s3 import S3Service
from models.experiments import Experiment, ExperimentCreate

router = APIRouter(
    prefix="/experiments",
    tags=['experiments'])


@router.get("/", response_model=List[Experiment])
async def get_experiments(
        test_type: str = None,
        service: ExperimentsService = Depends(get_experiments_service),
        username: str = Depends(get_current_username)
):
    """Просмотр всех файлов"""
    return await service.get(test_type)


@router.get("/test_types/")
async def get_test_types(
        service: ExperimentsService = Depends(get_experiments_service),
        username: str = Depends(get_current_username)
):
    """Просмотр всех файлов"""
    return await service.get_test_types()


@router.post("/", response_model=Experiment)
async def create_experiment(
        test_type: str,
        laboratory_number: str,
        object_number: str,
        description: str,
        experiment_file: UploadFile,
        service: ExperimentsService = Depends(get_experiments_service),
        s3_service: S3Service = Depends(get_s3_service),
        username: str = Depends(get_current_username)
):
    """Создание отчета"""
    contents = await experiment_file.read()
    filename = experiment_file.filename.replace(' ', '_')

    experiment = await service.create(
        ExperimentCreate(
            test_type=test_type,
            laboratory_number=laboratory_number,
            object_number=object_number,
            description=description
        ),
        filename
    )

    try:
        await s3_service.upload(data=contents, key=f'plotter/{experiment.id}_{filename}')
    except Exception as err:
        await service.delete(experiment.id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(err)
        )

    return experiment


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_experiment(
        id: int,
        service: ExperimentsService = Depends(get_experiments_service),
        s3_service: S3Service = Depends(get_s3_service),
        username: str = Depends(get_current_username)
):
    """Удаление файла"""
    key = await service.get_file(id)

    try:
        await s3_service.delete(key[0])
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(err)
        )

    await service.delete(id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


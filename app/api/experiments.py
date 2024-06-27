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

#@router.get("/", response_model=Report)
#@cache(expire=60)
#async def get_report(
#        id: str,
#        request: Request,
#        service: ReportsService = Depends(get_report_service),
#        stat_service: StatisticsService = Depends(get_statistics_service),
#):
#    """Просмотр данных отчета по id"""
#    report = await service.get(id)
#
#    if id != '4c795fb5002852b5af5df9e5de1e44b11b920d6f':
#        await stat_service.create(client_ip=request.headers.get("X-Real-IP") or request.client.host, report_id=id)
#
#    return report

@router.get("/", response_model=List[Experiment])
async def get_experiments(
        service: ExperimentsService = Depends(get_experiments_service),
        username: str = Depends(get_current_username)
):
    """Просмотр всех файлов"""
    return await service.get()

@router.post("/")
async def create_experiment(
        experiment_data: ExperimentCreate,
        experiment_file: UploadFile,
        service: ExperimentsService = Depends(get_experiments_service),
        s3_service: S3Service = Depends(get_s3_service),
        username: str = Depends(get_current_username)
):
    """Создание отчета"""
    experiment = await service.create(experiment_data)

    contents = await experiment_file.read()

    try:
        await s3_service.upload(data=contents, key=f'plotter/{experiment.id}.pickle')
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
    try:
        await s3_service.delete(f'plotter/{id}.pickle')
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(err)
        )

    await service.delete(id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


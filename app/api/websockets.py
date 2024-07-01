from fastapi import APIRouter, WebSocket, Depends
from starlette.websockets import WebSocketDisconnect
import asyncio
import pickle

from services.depends import get_experiments_service, get_s3_service
from services.experiments import ExperimentsService
from services.s3 import S3Service


router = APIRouter(
    prefix="/resonant_column",
    tags=['resonant_column'])


@router.websocket("/ws/{experiment_id}/")
async def websocket_endpoint(
        experiment_id: int,
        websocket: WebSocket,
        service: ExperimentsService = Depends(get_experiments_service),
        s3_service: S3Service = Depends(get_s3_service),
):
    key = await service.get_file(experiment_id)

    response = await s3_service.get(key[0])

    if 'Body' in response:
        body = response['Body']
        # Читаем все данные из тела как байты
        file_bytes = await body.read()

        # Десериализация данных из байтов
        experiment_data = pickle.loads(file_bytes)

    await websocket.accept()

    try:
        while True:
            for i in experiment_data["result_RCCT"].keys():
                print(experiment_data["result_RCCT"])
                for j in range(len(experiment_data["result_RCCT"][i]["Freq"])):
                    data = {
                        'x': experiment_data["result_RCCT"][i]["Freq"][j],
                        "y": experiment_data["result_RCCT"][i]["ShearStrain1[]"][j],
                    }
                    await websocket.send_json(data)
                    await asyncio.sleep(0.5)

                    print(experiment_data["result_RCCT"][i]["Freq"][j])

                data = {
                    "timestamp": experiment_data['ShearStrain1[]'][i],
                    "value": experiment_data['G1[MPa]'][i],
                    "frequency": experiment_data['Frequency1'][i],
                    "current": experiment_data['CURRENT[A]'][i],
                }

                await websocket.send_json(data)
                await asyncio.sleep(0.5)

            await websocket.close()
            break

    except WebSocketDisconnect:
        print("Client disconnected")



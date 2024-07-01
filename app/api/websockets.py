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
                for j in range(len(experiment_data["result_RCCT"][i]["Freq"])):
                    data = {
                        "Freq": experiment_data["result_RCCT"][i]["Freq"][j],
                        "Acur_target": experiment_data["result_RCCT"][i]["Acur_target"][j],
                        "Adac": experiment_data["result_RCCT"][i]["Adac"][j],
                        "ACCELERATION1": experiment_data["result_RCCT"][i]["ACCELERATION1[m/s^2]"][j],
                        "ACCELERATION2": experiment_data["result_RCCT"][i]["ACCELERATION2[m/s^2]"][j],
                        "CURRENT": experiment_data["result_RCCT"][i]["CURRENT[A]"][j],
                        "Velocity1": experiment_data["result_RCCT"][i]["Velocity1[m/s]"][j],
                        "Displacement1": experiment_data["result_RCCT"][i]["Displacement1[m]"][j],
                        "ShearStrain1": experiment_data["result_RCCT"][i]["ShearStrain1[]"][j],
                        "Velocity2": experiment_data["result_RCCT"][i]["Velocity2[m/s]"][j],
                        "Displacement2": experiment_data["result_RCCT"][i]["Displacement2[m]"][j],
                        "ShearStrain2": experiment_data["result_RCCT"][i]["ShearStrain2[]"][j],
                    }
                    await websocket.send_json(data)
                    await asyncio.sleep(0.1)


                data = {
                    "CURRENT_general": experiment_data['CURRENT[A]'][i],
                    "ShearStrain1_general": experiment_data['ShearStrain1[]'][i],
                    "G1": experiment_data['G1[MPa]'][i],
                    "Frequency1": experiment_data['Frequency1'][i],
                    "Frequency2": experiment_data['CURRENT[A]'][i],
                    "ShearStrain2_general": experiment_data['ShearStrain2[]'][i],
                    "G2": experiment_data['G2[MPa]'][i],
                }

                await websocket.send_json(data)
                await asyncio.sleep(0.1)

            await websocket.close()
            break

    except WebSocketDisconnect:
        print("Client disconnected")



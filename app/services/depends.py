from aiobotocore.session import get_session

from config import configs
from db.database import async_session
from services.experiments import ExperimentsService
from services.s3 import S3Service

async def get_experiments_service():
    async with async_session() as session:
        async with session.begin():
            try:
                yield ExperimentsService(session)
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

async def get_s3_service():
    session = get_session()
    async with session.create_client(
            's3',
            endpoint_url=configs.endpoint_url,
            region_name=configs.region_name,
            aws_secret_access_key=configs.aws_secret_access_key,
            aws_access_key_id=configs.aws_access_key_id
    ) as client:
        try:
            yield S3Service(client)
        except Exception as e:
            raise e
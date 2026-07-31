from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.sensor import Sensor
from ..schemas.sensor import SensorCreate


class SensorService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, system_id: int, data: SensorCreate):
        """Асинхронное создание нового датчика в системе космического корабля"""
        sensor = Sensor(
            system_id=system_id,
            name=data.name,
            unit=data.unit,
            min_normal=data.min_normal,
            max_normal=data.max_normal,
            value=data.value
        )
        self.db.add(sensor)

        await self.db.commit()
        await self.db.refresh(sensor)
        return sensor

    async def get_by_system(self, system_id: int):
        """Асинхронный поиск всех датчиков конкретной системы"""
        query = select(Sensor).filter(Sensor.system_id == system_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, sensor_id: int):
        """Асинхронный поиск датчика по его ID"""
        query = select(Sensor).filter(Sensor.id == sensor_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def update_value(self, sensor_id: int, value: float):
        """
        Асинхронно обновляет показания датчика и вычисляет смену состояний.
        """
        sensor = await self.get_by_id(sensor_id)
        if not sensor:
            return None

        old_status = "normal" if sensor.min_normal <= sensor.value <= sensor.max_normal else "abnormal"

        sensor.value = value

        new_status = "normal" if sensor.min_normal <= value <= sensor.max_normal else "abnormal"

        await self.db.commit()
        await self.db.refresh(sensor)

        return sensor, old_status, new_status

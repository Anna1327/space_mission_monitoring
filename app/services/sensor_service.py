from sqlalchemy.orm import Session
from ..models.sensor import Sensor
from ..schemas.sensor import SensorCreate


class SensorService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, system_id: int, data: SensorCreate):
        sensor = Sensor(
            system_id=system_id,
            name=data.name,
            unit=data.unit,
            min_normal=data.min_normal,
            max_normal=data.max_normal
        )
        self.db.add(sensor)
        self.db.commit()
        self.db.refresh(sensor)
        return sensor

    def get_by_system(self, system_id: int):
        return self.db.query(Sensor).filter(Sensor.system_id == system_id).all()

    def get_by_id(self, sensor_id: int):
        return self.db.query(Sensor).filter(Sensor.id == sensor_id).first()

    def update_value(self, sensor_id: int, value: float):
        sensor = self.get_by_id(sensor_id)
        if not sensor:
            return None
        old_status = "normal" if sensor.min_normal <= sensor.value <= sensor.max_normal else "abnormal"
        sensor.value = value
        new_status = "normal" if sensor.min_normal <= value <= sensor.max_normal else "abnormal"
        self.db.commit()
        self.db.refresh(sensor)
        return sensor, old_status, new_status

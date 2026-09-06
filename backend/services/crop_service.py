from typing import List, Optional
from sqlalchemy.orm import Session
from backend.models.crop import Crop, FarmerCrop
from backend.config import Config

class CropService:
    @staticmethod
    def list_crops(db: Session, season: Optional[str] = None, active_only: bool = True) -> List[Crop]:
        query = db.query(Crop)
        if active_only:
            query = query.filter(Crop.status == 'ACTIVE')
        if season and season != 'All':
            query = query.filter((Crop.season == season) | (Crop.season == 'All'))
        return query.order_by(Crop.name.asc()).all()

    @staticmethod
    def get_crop_by_id(db: Session, crop_id: int) -> Optional[Crop]:
        return db.query(Crop).filter(Crop.crop_id == crop_id).first()

    @staticmethod
    def get_eligible_crops_for_farmer(db: Session, farmer_id: str, season: Optional[str] = None) -> List[Crop]:
        """
        Returns crops registered to this farmer that match the current active season.
        Rule: Season-Based Crop Filtering at booking time (rules.md §5, PRD.md §10.3).
        """
        active_season = season or Config.CURRENT_SEASON
        # Query farmer's registered crops
        farmer_crop_ids = [fc.crop_id for fc in db.query(FarmerCrop).filter(FarmerCrop.farmer_id == farmer_id).all()]
        
        query = db.query(Crop).filter(Crop.status == 'ACTIVE')
        if farmer_crop_ids:
            query = query.filter(Crop.crop_id.in_(farmer_crop_ids))
        if active_season and active_season != 'All':
            query = query.filter((Crop.season == active_season) | (Crop.season == 'All'))

        return query.order_by(Crop.name.asc()).all()

    @staticmethod
    def create_crop(db: Session, data: dict) -> Crop:
        crop = Crop(
            name=data['name'].strip(),
            category=data.get('category', 'General').strip(),
            rate_per_quintal=data['rate_per_quintal'],
            time_to_unload_per_quintal_minutes=int(data.get('time_to_unload_per_quintal_minutes', 5)),
            season=data.get('season', 'Kharif').strip(),
            status=data.get('status', 'ACTIVE')
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)
        return crop

    @staticmethod
    def update_crop(db: Session, crop_id: int, data: dict) -> Optional[Crop]:
        crop = db.query(Crop).filter(Crop.crop_id == crop_id).first()
        if not crop:
            return None
        if 'name' in data:
            crop.name = data['name'].strip()
        if 'category' in data:
            crop.category = data['category'].strip()
        if 'rate_per_quintal' in data:
            crop.rate_per_quintal = data['rate_per_quintal']
        if 'time_to_unload_per_quintal_minutes' in data:
            crop.time_to_unload_per_quintal_minutes = int(data['time_to_unload_per_quintal_minutes'])
        if 'season' in data:
            crop.season = data['season'].strip()
        if 'status' in data:
            crop.status = data['status']
        db.commit()
        db.refresh(crop)
        return crop

    @staticmethod
    def delete_crop(db: Session, crop_id: int) -> bool:
        """Soft-deletes crop by setting status to INACTIVE."""
        crop = db.query(Crop).filter(Crop.crop_id == crop_id).first()
        if not crop:
            return False
        crop.status = 'INACTIVE'
        db.commit()
        return True

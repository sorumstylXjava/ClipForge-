from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
import secrets

class CRUDUser:
    def get(self, db: Session, id: Any) -> Optional[User]:
        return db.query(User).filter(User.id == id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        # Kalau password None (Google login), generate random hash
        raw_password = obj_in.password if obj_in.password else secrets.token_hex(32)
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(raw_password),
            full_name=obj_in.full_name,
            avatar_url=obj_in.avatar_url if hasattr(obj_in, 'avatar_url') else None,
            phone=obj_in.phone if hasattr(obj_in, 'phone') else None,
            plan=obj_in.plan if hasattr(obj_in, 'plan') and obj_in.plan else "free",
            ai_mode=obj_in.ai_mode if hasattr(obj_in, 'ai_mode') and obj_in.ai_mode else "server",
            preferred_lang=obj_in.preferred_lang if hasattr(obj_in, 'preferred_lang') and obj_in.preferred_lang else "en",
            preferred_resolution=obj_in.preferred_resolution if hasattr(obj_in, 'preferred_resolution') and obj_in.preferred_resolution else "720p",
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        for field in update_data:
            setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

user = CRUDUser()

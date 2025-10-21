from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models_sql.user import SqlUser
from app.schemas.auth import GetUserRequest

class MarketRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_users(self, request: GetUserRequest) -> List[SqlUser]:
        # mirror C#:
        # var sqlUsers = await _context.User.ToListAsync();
        # var filtered = sqlUsers.Where(su => request.UserName == "-1" || (
        #     su.Password == request.Password && su.UserName == request.UserName));
        users = self.db.execute(select(SqlUser)).scalars().all()
        if request.user_name == "-1":
            return users
        return [
            u for u in users
            if (u.UserName == request.user_name and u.Password == request.password)
        ]

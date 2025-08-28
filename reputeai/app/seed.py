from passlib.hash import argon2

from .db.session import SessionLocal
from .models import Membership, Org, OrgRole, User


def run() -> None:
    with SessionLocal() as db:
        if db.query(User).filter_by(email="demo@example.com").first():
            return
        user = User(email="demo@example.com", hashed_password=argon2.hash("password"), is_verified=True)
        org = Org(name="Demo Org")
        db.add_all([user, org])
        db.commit()
        db.refresh(user)
        db.refresh(org)
        membership = Membership(user_id=user.id, org_id=org.id, role=OrgRole.owner)
        db.add(membership)
        db.commit()
        print("Created demo user demo@example.com with password 'password'")


if __name__ == "__main__":
    run()

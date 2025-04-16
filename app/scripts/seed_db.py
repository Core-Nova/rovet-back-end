from datetime import datetime

from app.db.session import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole

def seed_users():
    db = SessionLocal()
    try:
        print("Successfully connected to the database")
        
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            print("Creating admin user...")
            admin = User(
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin",
                role=UserRole.ADMIN,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(admin)
            print("Admin user created successfully")
        else:
            print("Admin user already exists")

        team_users = [
            {
                "email": "luci@example.com",
                "password": "user123",
                "full_name": "Luci",
                "role": UserRole.USER
            },
            {
                "email": "eva@example.com",
                "password": "user123",
                "full_name": "Eva",
                "role": UserRole.USER
            },
            {
                "email": "tsetso@example.com",
                "password": "user123",
                "full_name": "Tsetso",
                "role": UserRole.USER
            },
            {
                "email": "nick@example.com",
                "password": "user123",
                "full_name": "Nick Bacon",
                "role": UserRole.USER
            },
            {
                "email": "rado@example.com",
                "password": "user123",
                "full_name": "Rado",
                "role": UserRole.USER
            },
            {
                "email": "kamen@example.com",
                "password": "user123",
                "full_name": "Kamen",
                "role": UserRole.USER
            },
            {
                "email": "mario@example.com",
                "password": "user123",
                "full_name": "Mario",
                "role": UserRole.USER
            }
        ]

        for user_data in team_users:
            print(f"Processing user: {user_data['email']}")
            user = db.query(User).filter(User.email == user_data["email"]).first()
            if not user:
                print(f"Creating user: {user_data['email']}")
                user = User(
                    email=user_data["email"],
                    hashed_password=get_password_hash(user_data["password"]),
                    full_name=user_data["full_name"],
                    role=user_data["role"],
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(user)
                print(f"User created successfully: {user_data['email']}")
            else:
                print(f"User already exists: {user_data['email']}")

        db.commit()
        print("Database seeded successfully!")
        
        user_count = db.query(User).count()
        print(f"Total users in database: {user_count}")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_users() 
import reflex as rx
from sqlmodel import Session, create_engine, select
from budget_erp.models.user import User
import bcrypt

def seed_user():
    engine = create_engine("sqlite:///reflex.db")
    with Session(engine) as session:
        # Check if user already exists
        statement = select(User).where(User.mail == "admin@example.com")
        existing_user = session.exec(statement).first()
        
        if existing_user:
            print("User admin@example.com already exists. Updating password...")
            user = existing_user
        else:
            print("Creating new user admin@example.com...")
            user = User(
                mail="admin@example.com",
                name="Admin User",
                role="admin",
                created_by=1,
                status="active"
            )
        
        # Hash password "password123"
        password = "password123"
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user.password = hashed.decode('utf-8')
        
        session.add(user)
        session.commit()
        print("Seed user created/updated successfully.")

if __name__ == "__main__":
    seed_user()

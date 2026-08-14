from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker


# -------------------------
# FastAPI
# -------------------------

app = FastAPI()


# -------------------------
# Static files
# -------------------------

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/app")
def app_page():
    return FileResponse("static/index.html")


# -------------------------
# Database
# -------------------------

DATABASE_URL = "sqlite:///./expenses.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class ExpenseDB(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)


Base.metadata.create_all(bind=engine)


# -------------------------
# Request model
# -------------------------

class Expense(BaseModel):
    name: str
    amount: float
    category: str


# -------------------------
# Home
# -------------------------

@app.get("/")
def home():
    return {
        "message": "Expense Tracker API is working!"
    }


# -------------------------
# Get all expenses
# -------------------------

@app.get("/expenses")
def get_expenses():
    db = SessionLocal()

    try:
        expenses = db.query(ExpenseDB).all()

        return [
            {
                "id": expense.id,
                "name": expense.name,
                "amount": expense.amount,
                "category": expense.category
            }
            for expense in expenses
        ]

    finally:
        db.close()


# -------------------------
# Add expense
# -------------------------

@app.post("/expenses")
def add_expense(expense: Expense):
    db = SessionLocal()

    try:
        new_expense = ExpenseDB(
            name=expense.name,
            amount=expense.amount,
            category=expense.category
        )

        db.add(new_expense)
        db.commit()
        db.refresh(new_expense)

        return {
            "id": new_expense.id,
            "name": new_expense.name,
            "amount": new_expense.amount,
            "category": new_expense.category
        }

    finally:
        db.close()


# -------------------------
# Get one expense
# -------------------------

@app.get("/expenses/{expense_id}")
def get_expense(expense_id: int):
    db = SessionLocal()

    try:
        expense = db.query(ExpenseDB).filter(
            ExpenseDB.id == expense_id
        ).first()

        if not expense:
            raise HTTPException(
                status_code=404,
                detail="Expense not found"
            )

        return {
            "id": expense.id,
            "name": expense.name,
            "amount": expense.amount,
            "category": expense.category
        }

    finally:
        db.close()


# -------------------------
# Delete expense
# -------------------------

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    db = SessionLocal()

    try:
        expense = db.query(ExpenseDB).filter(
            ExpenseDB.id == expense_id
        ).first()

        if not expense:
            raise HTTPException(
                status_code=404,
                detail="Expense not found"
            )

        db.delete(expense)
        db.commit()

        return {
            "message": "Expense deleted"
        }

    finally:
        db.close()
    
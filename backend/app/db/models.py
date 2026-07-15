from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    UserID = Column(Integer, primary_key=True, index=True)
    Name = Column(String, index=True)
    Email = Column(String, unique=True, index=True)
    Password = Column(String) # Hashed password
    MonthlyIncome = Column(Float)
    MonthlyExpenses = Column(Float)

    financial_profile = relationship("FinancialProfile", back_populates="user", uselist=False)
    loans = relationship("Loan", back_populates="user")
    ai_history = relationship("AIHistory", back_populates="user")
    ai_negotiations = relationship("AINegotiation", back_populates="user")


class FinancialProfile(Base):
    __tablename__ = "financial_profiles"

    ProfileID = Column(Integer, primary_key=True, index=True)
    UserID = Column(Integer, ForeignKey("users.UserID"), unique=True)
    EMI_Ratio = Column(Float)
    DTI_Ratio = Column(Float)
    MonthlySurplus = Column(Float)
    StressLevel = Column(String)

    user = relationship("User", back_populates="financial_profile")


class Loan(Base):
    __tablename__ = "loans"

    LoanID = Column(Integer, primary_key=True, index=True)
    UserID = Column(Integer, ForeignKey("users.UserID"))
    LenderName = Column(String)
    LoanType = Column(String)
    OutstandingAmount = Column(Float)
    InterestRate = Column(Float)
    EMI = Column(Float)
    OverdueMonths = Column(Integer)

    user = relationship("User", back_populates="loans")
    settlement_predictions = relationship("SettlementPrediction", back_populates="loan")
    ai_negotiations = relationship("AINegotiation", back_populates="loan")


class AIHistory(Base):
    __tablename__ = "ai_history"

    HistoryID = Column(Integer, primary_key=True, index=True)
    UserID = Column(Integer, ForeignKey("users.UserID"))
    GeneratedContent = Column(Text)
    QueryType = Column(String)
    Timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="ai_history")


class SettlementPrediction(Base):
    __tablename__ = "settlement_predictions"

    SettlementID = Column(Integer, primary_key=True, index=True)
    LoanID = Column(Integer, ForeignKey("loans.LoanID"))
    SuggestedSettlement = Column(Float)
    RiskCategory = Column(String)
    PredictedAmount = Column(Float)

    loan = relationship("Loan", back_populates="settlement_predictions")


class AINegotiation(Base):
    __tablename__ = "ai_negotiations"

    AI_ID = Column(Integer, primary_key=True, index=True)
    LoanID = Column(Integer, ForeignKey("loans.LoanID"))
    UserID = Column(Integer, ForeignKey("users.UserID"))
    NegotiationStrategy = Column(Text)
    NegotiationLetter = Column(Text)
    GeneratedDate = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="ai_negotiations")
    loan = relationship("Loan", back_populates="ai_negotiations")

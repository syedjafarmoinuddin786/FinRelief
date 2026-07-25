from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    UserID = Column(Integer, primary_key=True, index=True)
    Name = Column(String, index=True)
    Email = Column(String, unique=True, index=True)
    Password = Column(String)  # bcrypt hash
    MonthlyIncome = Column(Float)
    MonthlyExpenses = Column(Float)
    
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    reset_token = Column(String, nullable=True)
    totp_secret = Column(String, nullable=True)
    is_2fa_enabled = Column(Boolean, default=False)

    CreditScore = Column(Integer, nullable=True)
    Savings = Column(Float, nullable=True, default=0.0)
    EmploymentStatus = Column(String, nullable=True)
    ProfilePictureUrl = Column(String, nullable=True)
    FinancialGoals = Column(Text, nullable=True)

    financial_profile = relationship("FinancialProfile", back_populates="user", uselist=False)
    loans = relationship("Loan", back_populates="user")
    ai_history = relationship("AIHistory", back_populates="user")
    ai_negotiations = relationship("AINegotiation", back_populates="user")
    settings = relationship("Setting", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")


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
    StartDate = Column(DateTime, nullable=True)
    DueDate = Column(DateTime, nullable=True)
    Status = Column(String, default="Active")

    user = relationship("User", back_populates="loans")
    settlement_predictions = relationship("SettlementPrediction", back_populates="loan")
    ai_negotiations = relationship("AINegotiation", back_populates="loan")


class SettlementPrediction(Base):
    __tablename__ = "settlement_predictions"
    SettlementID = Column(Integer, primary_key=True, index=True)
    LoanID = Column(Integer, ForeignKey("loans.LoanID"))
    SuggestedSettlement = Column(Float)
    RiskCategory = Column(String)
    PredictedAmount = Column(Float)

    loan = relationship("Loan", back_populates="settlement_predictions")


class AIHistory(Base):
    __tablename__ = "ai_history"
    HistoryID = Column(Integer, primary_key=True, index=True)
    UserID = Column(Integer, ForeignKey("users.UserID"))
    GeneratedContent = Column(Text)
    QueryType = Column(String)
    Timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    user = relationship("User", back_populates="ai_history")


class AINegotiation(Base):
    __tablename__ = "ai_negotiations"
    AI_ID = Column(Integer, primary_key=True, index=True)
    LoanID = Column(Integer, ForeignKey("loans.LoanID"))
    UserID = Column(Integer, ForeignKey("users.UserID"))
    NegotiationStrategy = Column(Text)
    NegotiationLetter = Column(Text)
    GeneratedDate = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    user = relationship("User", back_populates="ai_negotiations")
    loan = relationship("Loan", back_populates="ai_negotiations")

class Setting(Base):
    __tablename__ = "settings"
    SettingID = Column(Integer, primary_key=True, index=True)
    UserID = Column(Integer, ForeignKey("users.UserID"), unique=True)
    Theme = Column(String, default="light")
    Currency = Column(String, default="USD")
    Language = Column(String, default="en")
    NotificationsEnabled = Column(Boolean, default=True)

    user = relationship("User", back_populates="settings")

class Notification(Base):
    __tablename__ = "notifications"
    NotificationID = Column(Integer, primary_key=True, index=True)
    UserID = Column(Integer, ForeignKey("users.UserID"))
    Title = Column(String)
    Message = Column(Text)
    IsRead = Column(Boolean, default=False)
    Type = Column(String)
    CreatedAt = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    user = relationship("User", back_populates="notifications")

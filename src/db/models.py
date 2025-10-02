from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, ForeignKey, Date, Numeric, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Investor(Base):
    __tablename__ = "investors"
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    type = Column(Text)
    website = Column(Text, nullable=False)
    focus = Column(Text)
    portfolio_url = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("name", "website"),)

    funding_rounds = relationship("FundingRound", back_populates="investor")

class Startup(Base):
    __tablename__ = "startups"
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    website = Column(Text, nullable=False)
    sector = Column(Text)
    country = Column(Text)
    founded_year = Column(Integer)
    ai_or_accelerated_computing = Column(Boolean)
    nvidia_stack_alignment = Column(Boolean)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("name", "website"),)

    funding_rounds = relationship("FundingRound", back_populates="startup")
    leadership = relationship("Leadership", back_populates="startup")

class FundingRound(Base):
    __tablename__ = "funding_rounds"
    id = Column(Integer, primary_key=True)
    startup_id = Column(Integer, ForeignKey("startups.id"))
    investor_id = Column(Integer, ForeignKey("investors.id"))
    amount = Column(Numeric)
    round_date = Column(Date)
    round_type = Column(Text)

    __table_args__ = (UniqueConstraint("startup_id", "investor_id", "round_date"),)

    startup = relationship("Startup", back_populates="funding_rounds")
    investor = relationship("Investor", back_populates="funding_rounds")

class Leadership(Base):
    __tablename__ = "leadership"
    id = Column(Integer, primary_key=True)
    startup_id = Column(Integer, ForeignKey("startups.id"))
    name = Column(Text)
    role = Column(Text)
    linkedin = Column(Text)

    __table_args__ = (UniqueConstraint("startup_id", "name", "role"),)

    startup = relationship("Startup", back_populates="leadership")

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database.db import Base
import datetime

class DBInvoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, unique=True, index=True)
    invoice_number = Column(String, index=True, nullable=True)
    date = Column(String, nullable=True)
    
    seller_name = Column(String, nullable=True)
    seller_gst = Column(String, nullable=True)
    buyer_name = Column(String, nullable=True)
    buyer_gst = Column(String, nullable=True)
    
    subtotal = Column(Float, nullable=True)
    tax_amount = Column(Float, nullable=True)
    total_amount = Column(Float, nullable=True)
    
    validation_status = Column(String, default="pending")
    processing_time = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    line_items = relationship("DBLineItem", back_populates="invoice")

class DBLineItem(Base):
    __tablename__ = "line_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    
    description = Column(String)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, nullable=True)
    total = Column(Float, nullable=True)

    invoice = relationship("DBInvoice", back_populates="line_items")

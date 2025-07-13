from sqlalchemy import Column, String, DECIMAL, Integer, Boolean, ARRAY, DateTime, func
from sqlalchemy.orm import relationship
from ..core.db.database import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(String(50), primary_key=True)  # e.g., 'free', 'basic', 'premium'
    name = Column(String(255), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=True)
    currency = Column(String(3), default='NOK')
    max_submissions = Column(Integer, nullable=False)
    features = Column(ARRAY(String), nullable=True)  # Array of feature descriptions
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships - temporarily disabled to avoid circular dependencies
    # customer_infos = relationship("CustomerInfo", back_populates="subscription_plan")
    
    def __repr__(self):
        return f"<SubscriptionPlan(id='{self.id}', name='{self.name}', price={self.price}, max_submissions={self.max_submissions})>"

from datetime import datetime
from typing import Optional
from enum import Enum


class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class PaymentMethod(Enum):
    """Payment method enumeration"""
    QR = "qr"
    UPI = "upi"


class Payment:
    """Payment model for database storage"""
    
    def __init__(self, payment_id: str, user_id: int, amount: float, method: PaymentMethod):
        self.payment_id = payment_id
        self.user_id = user_id
        self.amount = amount
        self.method = method.value if isinstance(method, PaymentMethod) else method
        self.status = PaymentStatus.PENDING.value
        self.screenshot_file_id: Optional[str] = None
        self.utr: Optional[str] = None
        self.notes: str = ""
        self.points_granted: int = 0
        self.created_at = datetime.now().isoformat()
        self.approved_at: Optional[str] = None
        self.approved_by: Optional[int] = None
    
    def to_dict(self) -> dict:
        """Convert payment to dictionary"""
        return {
            "payment_id": self.payment_id,
            "user_id": self.user_id,
            "amount": self.amount,
            "method": self.method,
            "status": self.status,
            "screenshot_file_id": self.screenshot_file_id,
            "utr": self.utr,
            "notes": self.notes,
            "points_granted": self.points_granted,
            "created_at": self.created_at,
            "approved_at": self.approved_at,
            "approved_by": self.approved_by
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Payment':
        """Create payment from dictionary"""
        payment = Payment(
            data['payment_id'],
            data['user_id'],
            data['amount'],
            data.get('method', 'qr')
        )
        payment.status = data.get('status', PaymentStatus.PENDING.value)
        payment.screenshot_file_id = data.get('screenshot_file_id')
        payment.utr = data.get('utr')
        payment.notes = data.get('notes', '')
        payment.points_granted = data.get('points_granted', 0)
        payment.created_at = data.get('created_at', datetime.now().isoformat())
        payment.approved_at = data.get('approved_at')
        payment.approved_by = data.get('approved_by')
        return payment
    
    def approve(self, admin_id: int, points: int) -> None:
        """Approve payment"""
        self.status = PaymentStatus.APPROVED.value
        self.points_granted = points
        self.approved_at = datetime.now().isoformat()
        self.approved_by = admin_id
    
    def reject(self, admin_id: int, reason: str) -> None:
        """Reject payment"""
        self.status = PaymentStatus.REJECTED.value
        self.notes = reason
        self.approved_at = datetime.now().isoformat()
        self.approved_by = admin_id
    
    def complete(self) -> None:
        """Mark payment as completed"""
        self.status = PaymentStatus.COMPLETED.value

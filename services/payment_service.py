from typing import Optional, List, Dict
from datetime import datetime
from utils.database import Database
from models.payment import Payment, PaymentStatus, PaymentMethod
from utils.logger import error_logger
import uuid


class PaymentService:
    """Payment processing service"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create_payment(self, user_id: int, amount: float, method: PaymentMethod) -> Payment:
        """Create new payment"""
        try:
            payment_id = f"PAY_{uuid.uuid4().hex[:12].upper()}"
            payment = Payment(payment_id, user_id, amount, method)
            
            data = self.db.load()
            if 'payments' not in data:
                data['payments'] = []
            
            data['payments'].append(payment.to_dict())
            self.db.save(data)
            
            return payment
        except Exception as e:
            error_logger.error(f"Failed to create payment: {e}")
            raise
    
    def get_payment(self, payment_id: str) -> Optional[Payment]:
        """Get payment by ID"""
        try:
            data = self.db.load()
            payments = data.get('payments', [])
            
            for payment_data in payments:
                if payment_data['payment_id'] == payment_id:
                    return Payment.from_dict(payment_data)
            
            return None
        except Exception as e:
            error_logger.error(f"Failed to get payment: {e}")
            return None
    
    def get_user_payments(self, user_id: int) -> List[Payment]:
        """Get all payments for user"""
        try:
            data = self.db.load()
            payments = data.get('payments', [])
            
            user_payments = []
            for payment_data in payments:
                if payment_data['user_id'] == user_id:
                    user_payments.append(Payment.from_dict(payment_data))
            
            return user_payments
        except Exception as e:
            error_logger.error(f"Failed to get user payments: {e}")
            return []
    
    def get_all_payments(self) -> List[Payment]:
        """Get all payments"""
        try:
            data = self.db.load()
            payments = data.get('payments', [])
            return [Payment.from_dict(p) for p in payments]
        except Exception as e:
            error_logger.error(f"Failed to get all payments: {e}")
            return []
    
    def update_payment(self, payment: Payment) -> None:
        """Update payment"""
        try:
            data = self.db.load()
            payments = data.get('payments', [])
            
            for i, p in enumerate(payments):
                if p['payment_id'] == payment.payment_id:
                    payments[i] = payment.to_dict()
                    break
            
            data['payments'] = payments
            self.db.save(data)
        except Exception as e:
            error_logger.error(f"Failed to update payment: {e}")
            raise
    
    def approve_payment(self, payment_id: str, admin_id: int, points: int) -> bool:
        """Approve payment and grant points"""
        try:
            payment = self.get_payment(payment_id)
            if not payment:
                return False
            
            payment.approve(admin_id, points)
            self.update_payment(payment)
            return True
        except Exception as e:
            error_logger.error(f"Failed to approve payment: {e}")
            return False
    
    def reject_payment(self, payment_id: str, admin_id: int, reason: str) -> bool:
        """Reject payment"""
        try:
            payment = self.get_payment(payment_id)
            if not payment:
                return False
            
            payment.reject(admin_id, reason)
            self.update_payment(payment)
            return True
        except Exception as e:
            error_logger.error(f"Failed to reject payment: {e}")
            return False
    
    def get_pending_payments(self) -> List[Payment]:
        """Get all pending payments"""
        try:
            payments = self.get_all_payments()
            return [p for p in payments if p.status == PaymentStatus.PENDING.value]
        except Exception as e:
            error_logger.error(f"Failed to get pending payments: {e}")
            return []
    
    def get_revenue(self) -> float:
        """Get total approved revenue"""
        try:
            payments = self.get_all_payments()
            approved = [p for p in payments if p.status == PaymentStatus.APPROVED.value]
            return sum(p.amount for p in approved)
        except Exception as e:
            error_logger.error(f"Failed to get revenue: {e}")
            return 0.0
    
    def get_payment_stats(self) -> Dict:
        """Get payment statistics"""
        try:
            payments = self.get_all_payments()
            
            pending = [p for p in payments if p.status == PaymentStatus.PENDING.value]
            approved = [p for p in payments if p.status == PaymentStatus.APPROVED.value]
            rejected = [p for p in payments if p.status == PaymentStatus.REJECTED.value]
            
            qr_payments = [p for p in payments if p.method == PaymentMethod.QR.value]
            upi_payments = [p for p in payments if p.method == PaymentMethod.UPI.value]
            
            return {
                'total_payments': len(payments),
                'pending': len(pending),
                'approved': len(approved),
                'rejected': len(rejected),
                'qr_payments': len(qr_payments),
                'upi_payments': len(upi_payments),
                'total_revenue': sum(p.amount for p in approved),
                'pending_amount': sum(p.amount for p in pending),
                'total_points_granted': sum(p.points_granted for p in approved)
            }
        except Exception as e:
            error_logger.error(f"Failed to get payment stats: {e}")
            return {}

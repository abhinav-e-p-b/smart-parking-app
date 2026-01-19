import os
import logging
from typing import Optional, Dict, List
from datetime import datetime
from twilio.rest import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwilioSMSService:
    """
    Twilio-based SMS notification service
    Handles sending parking assignment confirmations, tokens, and updates
    """
    
    def __init__(self):
        """Initialize Twilio client with credentials"""
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            logger.warning("Twilio credentials not fully configured")
            self.client = None
        else:
            self.client = Client(self.account_sid, self.auth_token)
            logger.info("Twilio SMS service initialized")
        
        self.message_log: List[Dict] = []
    
    def send_assignment_notification(
        self,
        phone_number: str,
        plate_number: str,
        lot_name: str,
        assigned_slot: str,
        token_number: str,
        estimated_cost: float,
        distance_km: float
    ) -> bool:
        """
        Send parking assignment notification via SMS
        
        Args:
            phone_number: Recipient phone number
            plate_number: Vehicle license plate
            lot_name: Name of assigned parking lot
            assigned_slot: Assigned parking slot
            token_number: Parking token/receipt number
            estimated_cost: Estimated parking cost
            distance_km: Distance to parking lot
            
        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            message_body = self._format_assignment_message(
                plate_number, lot_name, assigned_slot, token_number, estimated_cost, distance_km
            )
            
            return self._send_sms(phone_number, message_body, "assignment")
            
        except Exception as e:
            logger.error(f"Error sending assignment notification: {str(e)}")
            return False
    
    def send_token_reminder(
        self,
        phone_number: str,
        token_number: str,
        lot_name: str,
        slot_number: str,
        remaining_time_minutes: int
    ) -> bool:
        """
        Send token/receipt reminder SMS
        
        Args:
            phone_number: Recipient phone number
            token_number: Parking token
            lot_name: Parking lot name
            slot_number: Parking slot
            remaining_time_minutes: Remaining parking time
            
        Returns:
            True if message sent successfully
        """
        try:
            message_body = f"""Your parking token:

Token: {token_number}
Lot: {lot_name}
Slot: {slot_number}
Time Left: {remaining_time_minutes} mins

Please keep your token safe. You'll need it to exit.
For support: +1-XXX-PARKING"""
            
            return self._send_sms(phone_number, message_body, "token_reminder")
            
        except Exception as e:
            logger.error(f"Error sending token reminder: {str(e)}")
            return False
    
    def send_time_expiry_warning(
        self,
        phone_number: str,
        token_number: str,
        lot_name: str,
        minutes_until_expiry: int
    ) -> bool:
        """
        Send warning when parking time is about to expire
        
        Args:
            phone_number: Recipient phone number
            token_number: Parking token
            lot_name: Parking lot name
            minutes_until_expiry: Minutes until parking expires
            
        Returns:
            True if message sent successfully
        """
        try:
            message_body = f"""PARKING TIME EXPIRY WARNING

Token: {token_number}
Lot: {lot_name}
Expires in: {minutes_until_expiry} minutes

Please move your vehicle or extend parking time.
Link to extend: https://smartpark.local/extend/{token_number}"""
            
            return self._send_sms(phone_number, message_body, "expiry_warning")
            
        except Exception as e:
            logger.error(f"Error sending expiry warning: {str(e)}")
            return False
    
    def send_payment_receipt(
        self,
        phone_number: str,
        token_number: str,
        lot_name: str,
        parking_duration_minutes: int,
        amount_paid: float,
        payment_method: str
    ) -> bool:
        """
        Send payment receipt after parking
        
        Args:
            phone_number: Recipient phone number
            token_number: Parking token
            lot_name: Parking lot name
            parking_duration_minutes: Total parking duration
            amount_paid: Amount charged
            payment_method: Payment method used
            
        Returns:
            True if message sent successfully
        """
        try:
            hours = parking_duration_minutes // 60
            minutes = parking_duration_minutes % 60
            duration_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
            
            message_body = f"""PARKING RECEIPT

Token: {token_number}
Lot: {lot_name}
Duration: {duration_str}
Amount: ${amount_paid:.2f}
Method: {payment_method}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Thank you for using SmartParking!
Rate us: https://smartpark.local/rate/{token_number}"""
            
            return self._send_sms(phone_number, message_body, "receipt")
            
        except Exception as e:
            logger.error(f"Error sending receipt: {str(e)}")
            return False
    
    def send_emergency_notification(
        self,
        phone_number: str,
        message: str,
        token_number: Optional[str] = None
    ) -> bool:
        """
        Send emergency/alert notification
        
        Args:
            phone_number: Recipient phone number
            message: Alert message
            token_number: Optional parking token
            
        Returns:
            True if message sent successfully
        """
        try:
            full_message = f"ALERT: {message}"
            if token_number:
                full_message += f"\nToken: {token_number}"
            full_message += "\n\nContact support: +1-XXX-PARKING"
            
            return self._send_sms(phone_number, full_message, "emergency")
            
        except Exception as e:
            logger.error(f"Error sending emergency notification: {str(e)}")
            return False
    
    def _send_sms(self, phone_number: str, message_body: str, message_type: str) -> bool:
        """
        Internal method to send SMS via Twilio
        
        Args:
            phone_number: Recipient phone number
            message_body: Message content
            message_type: Type of message (for logging)
            
        Returns:
            True if sent successfully
        """
        if not self.client:
            logger.warning(f"Twilio client not initialized, message not sent: {message_type}")
            return False
        
        try:
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=phone_number
            )
            
            logger.info(f"SMS sent successfully. SID: {message.sid}, Type: {message_type}")
            
            # Log message
            self.message_log.append({
                'timestamp': datetime.now().isoformat(),
                'type': message_type,
                'to': phone_number,
                'status': 'sent',
                'sid': message.sid
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            
            self.message_log.append({
                'timestamp': datetime.now().isoformat(),
                'type': message_type,
                'to': phone_number,
                'status': 'failed',
                'error': str(e)
            })
            
            return False
    
    def _format_assignment_message(
        self,
        plate_number: str,
        lot_name: str,
        assigned_slot: str,
        token_number: str,
        estimated_cost: float,
        distance_km: float
    ) -> str:
        """Format parking assignment message"""
        return f"""PARKING ASSIGNED

Vehicle: {plate_number}
Lot: {lot_name}
Slot: {assigned_slot}
Distance: {distance_km} km
Estimated Cost: ${estimated_cost:.2f}

TOKEN: {token_number}

Please proceed to your assigned slot.
For support: +1-XXX-PARKING"""
    
    def get_message_log(self, limit: int = 50) -> List[Dict]:
        """Get recent message logs"""
        return self.message_log[-limit:]
    
    def get_message_stats(self) -> Dict:
        """Get message statistics"""
        total = len(self.message_log)
        sent = len([m for m in self.message_log if m['status'] == 'sent'])
        failed = len([m for m in self.message_log if m['status'] == 'failed'])
        
        by_type = {}
        for msg in self.message_log:
            msg_type = msg['type']
            by_type[msg_type] = by_type.get(msg_type, 0) + 1
        
        return {
            'total_messages': total,
            'sent': sent,
            'failed': failed,
            'by_type': by_type
        }


# Singleton instance
_sms_service = None

def get_sms_service() -> TwilioSMSService:
    """Get or create singleton SMS service"""
    global _sms_service
    if _sms_service is None:
        _sms_service = TwilioSMSService()
    return _sms_service

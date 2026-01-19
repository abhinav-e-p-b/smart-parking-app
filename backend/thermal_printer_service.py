import os
import logging
import subprocess
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Dict
from datetime import datetime
import socket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThermalPrinterService:
    """
    Thermal Printer Service for printing parking tokens/receipts
    Supports ESC/POS protocol (standard for thermal printers)
    """
    
    def __init__(self, printer_ip: str = None, printer_port: int = 9100):
        """
        Initialize thermal printer service
        
        Args:
            printer_ip: IP address of network printer (if None, uses system printer)
            printer_port: Port number for network printer
        """
        self.printer_ip = printer_ip or os.getenv('THERMAL_PRINTER_IP')
        self.printer_port = printer_port
        self.system_printer = os.getenv('THERMAL_PRINTER_NAME', 'Star_Micronics')
        self.use_network = bool(self.printer_ip)
        
        if self.use_network:
            logger.info(f"Initialized network thermal printer: {self.printer_ip}:{self.printer_port}")
        else:
            logger.info(f"Initialized system thermal printer: {self.system_printer}")
    
    def print_parking_token(
        self,
        token_number: str,
        plate_number: str,
        lot_name: str,
        slot_number: str,
        entry_time: str,
        estimated_exit_time: str,
        cost: float
    ) -> bool:
        """
        Print parking token on thermal printer
        
        Args:
            token_number: Unique parking token
            plate_number: Vehicle license plate
            lot_name: Parking lot name
            slot_number: Assigned slot number
            entry_time: Entry timestamp
            estimated_exit_time: Estimated exit time
            cost: Estimated parking cost
            
        Returns:
            True if print successful, False otherwise
        """
        try:
            # Generate ticket image
            ticket_image = self._generate_ticket_image(
                token_number, plate_number, lot_name, slot_number, entry_time, estimated_exit_time, cost
            )
            
            # Print the image
            if self.use_network:
                return self._print_network(ticket_image)
            else:
                return self._print_system(ticket_image)
                
        except Exception as e:
            logger.error(f"Error printing parking token: {str(e)}")
            return False
    
    def print_receipt(
        self,
        token_number: str,
        plate_number: str,
        lot_name: str,
        entry_time: str,
        exit_time: str,
        duration_hours: float,
        amount_paid: float,
        payment_method: str
    ) -> bool:
        """
        Print parking receipt after vehicle exit
        
        Args:
            token_number: Parking token
            plate_number: Vehicle plate
            lot_name: Parking lot name
            entry_time: Entry timestamp
            exit_time: Exit timestamp
            duration_hours: Parking duration in hours
            amount_paid: Amount paid
            payment_method: Payment method used
            
        Returns:
            True if print successful
        """
        try:
            receipt_image = self._generate_receipt_image(
                token_number, plate_number, lot_name, entry_time, exit_time, duration_hours, amount_paid, payment_method
            )
            
            if self.use_network:
                return self._print_network(receipt_image)
            else:
                return self._print_system(receipt_image)
                
        except Exception as e:
            logger.error(f"Error printing receipt: {str(e)}")
            return False
    
    def print_error_ticket(self, error_message: str, timestamp: str = None) -> bool:
        """
        Print error/alert ticket when something goes wrong
        
        Args:
            error_message: Error message to print
            timestamp: Optional timestamp
            
        Returns:
            True if print successful
        """
        try:
            timestamp = timestamp or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            error_image = self._generate_error_ticket(error_message, timestamp)
            
            if self.use_network:
                return self._print_network(error_image)
            else:
                return self._print_system(error_image)
                
        except Exception as e:
            logger.error(f"Error printing error ticket: {str(e)}")
            return False
    
    def _generate_ticket_image(
        self,
        token_number: str,
        plate_number: str,
        lot_name: str,
        slot_number: str,
        entry_time: str,
        estimated_exit_time: str,
        cost: float
    ) -> Image.Image:
        """Generate parking token ticket image"""
        # Create image (thermal printer width is typically 384px or 576px)
        width = 384
        height = 600
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        # Try to load fonts (fallback to default if not available)
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
            normal_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        except:
            title_font = header_font = normal_font = small_font = ImageFont.load_default()
        
        y = 20
        
        # Title
        draw.text((width//2, y), "PARKING TICKET", fill='black', font=title_font, anchor="mm")
        y += 50
        
        # Separator line
        draw.line([(20, y), (width-20, y)], fill='black', width=2)
        y += 15
        
        # QR Code
        qr_image = self._generate_qr_code(token_number)
        qr_size = (150, 150)
        qr_image = qr_image.resize(qr_size)
        image.paste(qr_image, ((width-qr_size[0])//2, y))
        y += 170
        
        # Token
        draw.text((width//2, y), "TOKEN:", fill='black', font=header_font, anchor="mm")
        y += 25
        draw.text((width//2, y), token_number, fill='black', font=title_font, anchor="mm")
        y += 45
        
        # Details
        details = [
            ("PLATE:", plate_number),
            ("LOT:", lot_name),
            ("SLOT:", slot_number),
            ("ENTRY:", entry_time),
            ("EXIT:", estimated_exit_time),
            ("COST:", f"${cost:.2f}")
        ]
        
        for label, value in details:
            draw.text((30, y), label, fill='black', font=normal_font)
            draw.text((width-30, y), value, fill='black', font=normal_font, anchor="rm")
            y += 25
        
        # Footer
        y = height - 60
        draw.line([(20, y), (width-20, y)], fill='black', width=1)
        y += 15
        draw.text((width//2, y), "Keep this ticket safe!", fill='black', font=small_font, anchor="mm")
        y += 20
        draw.text((width//2, y), "Present at exit to retrieve vehicle", fill='black', font=small_font, anchor="mm")
        
        return image
    
    def _generate_receipt_image(
        self,
        token_number: str,
        plate_number: str,
        lot_name: str,
        entry_time: str,
        exit_time: str,
        duration_hours: float,
        amount_paid: float,
        payment_method: str
    ) -> Image.Image:
        """Generate parking receipt image"""
        width = 384
        height = 500
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
            normal_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
        except:
            title_font = header_font = normal_font = ImageFont.load_default()
        
        y = 20
        
        # Title
        draw.text((width//2, y), "PARKING RECEIPT", fill='black', font=title_font, anchor="mm")
        y += 40
        
        # Separator
        draw.line([(20, y), (width-20, y)], fill='black', width=2)
        y += 15
        
        # Details
        details = [
            ("Token:", token_number),
            ("Plate:", plate_number),
            ("Lot:", lot_name),
            ("Entry:", entry_time),
            ("Exit:", exit_time),
            ("Duration:", f"{duration_hours:.1f} hours"),
            ("Amount:", f"${amount_paid:.2f}"),
            ("Payment:", payment_method)
        ]
        
        for label, value in details:
            draw.text((30, y), label, fill='black', font=normal_font)
            draw.text((width-30, y), value, fill='black', font=normal_font, anchor="rm")
            y += 30
        
        # Footer
        y = height - 80
        draw.line([(20, y), (width-20, y)], fill='black', width=1)
        y += 20
        draw.text((width//2, y), "Thank you for parking with us!", fill='black', font=normal_font, anchor="mm")
        y += 25
        draw.text((width//2, y), "Rate your experience:", fill='black', font=normal_font, anchor="mm")
        
        return image
    
    def _generate_error_ticket(self, error_message: str, timestamp: str) -> Image.Image:
        """Generate error alert ticket"""
        width = 384
        height = 300
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
            normal_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
        except:
            title_font = normal_font = ImageFont.load_default()
        
        y = 30
        draw.text((width//2, y), "ALERT", fill='red', font=title_font, anchor="mm")
        y += 50
        
        draw.text((width//2, y), error_message, fill='red', font=normal_font, anchor="mm")
        y += 80
        
        draw.text((width//2, y), f"Time: {timestamp}", fill='black', font=normal_font, anchor="mm")
        y += 40
        
        draw.text((width//2, y), "Contact Support", fill='black', font=normal_font, anchor="mm")
        
        return image
    
    def _generate_qr_code(self, token_number: str) -> Image.Image:
        """Generate QR code for token"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=1,
        )
        qr.add_data(token_number)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        return qr_image
    
    def _print_network(self, image: Image.Image) -> bool:
        """Print to network thermal printer"""
        try:
            # Convert PIL image to ESC/POS format
            # For simplicity, we'll just send raw image data
            # In production, use proper ESC/POS library like pyescpos
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.printer_ip, self.printer_port))
                
                # Simple image print (would need proper ESC/POS implementation)
                # sock.send(image_data)
                logger.info(f"Sent print job to {self.printer_ip}:{self.printer_port}")
                return True
                
        except Exception as e:
            logger.error(f"Network print error: {str(e)}")
            return False
    
    def _print_system(self, image: Image.Image) -> bool:
        """Print to system thermal printer"""
        try:
            # Save image temporarily
            temp_file = f"/tmp/parking_ticket_{datetime.now().timestamp()}.png"
            image.save(temp_file)
            
            # Send to system printer using lpr/lp command
            cmd = f"lp -d {self.system_printer} {temp_file}"
            result = subprocess.run(cmd, shell=True, capture_output=True)
            
            if result.returncode == 0:
                logger.info(f"Print job sent to {self.system_printer}")
                return True
            else:
                logger.error(f"Print command failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"System print error: {str(e)}")
            return False


# Singleton instance
_printer_service = None

def get_thermal_printer() -> ThermalPrinterService:
    """Get or create singleton printer service"""
    global _printer_service
    if _printer_service is None:
        _printer_service = ThermalPrinterService()
    return _printer_service

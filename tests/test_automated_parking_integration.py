import pytest
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ocr_service import NumberPlateOCR
from backend.parking_assignment_engine import (
    ParkingAssignmentEngine, ParkingLot, VehicleInfo
)
from backend.twilio_service import TwilioSMSService
from backend.thermal_printer_service import ThermalPrinterService


class TestAutomatedParkingIntegration:
    """Integration tests for automated parking system"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        # Initialize services
        self.ocr = NumberPlateOCR()
        self.assignment_engine = ParkingAssignmentEngine()
        self.sms_service = TwilioSMSService()
        self.printer_service = ThermalPrinterService()

        # Register test parking lots
        self._setup_test_lots()

    def _setup_test_lots(self):
        """Setup test parking lots"""
        lots = [
            ParkingLot(
                lot_id=1,
                name="Central Garage",
                latitude=40.7128,
                longitude=-74.006,
                available_slots=45,
                total_slots=200,
                price_per_hour=5.5,
                traffic_level="Low",
                rating=4.5
            ),
            ParkingLot(
                lot_id=2,
                name="Downtown Lot",
                latitude=40.7138,
                longitude=-74.0015,
                available_slots=12,
                total_slots=85,
                price_per_hour=4.0,
                traffic_level="Medium",
                rating=4.2
            ),
            ParkingLot(
                lot_id=3,
                name="Riverside Parking",
                latitude=40.7158,
                longitude=-74.0035,
                available_slots=156,
                total_slots=400,
                price_per_hour=2.75,
                traffic_level="Low",
                rating=3.8
            ),
        ]

        for lot in lots:
            self.assignment_engine.register_parking_lot(lot)

    # ==================== OCR Tests ====================

    def test_ocr_service_initialization(self):
        """Test OCR service initializes correctly"""
        assert self.ocr is not None
        assert self.ocr.reader is not None

    def test_ocr_clean_plate_text(self):
        """Test plate text cleaning and validation"""
        test_cases = [
            ("DL01AB1234", "DL01AB1234"),
            ("DL 01 AB 1234", "DL01AB1234"),
            ("DL@01#AB$1234", "DL01AB1234"),
            ("KA 51 AB 1234", "KA51AB1234"),
            ("ABC1234", "ABC1234"),
        ]

        for input_text, expected in test_cases:
            result = self.ocr._clean_plate_text(input_text)
            assert result == expected, f"Failed for {input_text}"

    # ==================== Parking Assignment Tests ====================

    def test_assignment_engine_initialization(self):
        """Test assignment engine initializes with lots"""
        assert len(self.assignment_engine.parking_lots) == 3
        assert 1 in self.assignment_engine.parking_lots

    def test_distance_calculation(self):
        """Test distance calculation between coordinates"""
        # New York coordinates
        lat1, lon1 = 40.7128, -74.0060
        # Approximately 1km away
        lat2, lon2 = 40.7200, -74.0060

        distance = self.assignment_engine.calculate_distance(lat1, lon1, lat2, lon2)
        
        # Should be approximately 0.8 km
        assert 0.7 < distance < 0.9, f"Distance calculation error: {distance}"

    def test_lot_scoring(self):
        """Test parking lot scoring"""
        vehicle = VehicleInfo(
            plate_number="DL01AB1234",
            latitude=40.7128,
            longitude=-74.0060,
            vehicle_type="car"
        )

        lot = self.assignment_engine.parking_lots[1]
        score = self.assignment_engine.score_lot(lot, vehicle)

        assert 0 <= score <= 1, "Score should be between 0 and 1"
        assert score > 0.5, "Score should be reasonable for available lot"

    def test_top_candidates_selection(self):
        """Test selection of top candidate parking lots"""
        vehicle = VehicleInfo(
            plate_number="DL01AB1234",
            latitude=40.7128,
            longitude=-74.0060,
            vehicle_type="car"
        )

        candidates = self.assignment_engine.get_top_candidates(vehicle, top_n=2)

        assert len(candidates) <= 2, "Should return at most 2 candidates"
        assert len(candidates) > 0, "Should return at least 1 candidate"
        
        # Verify candidates are sorted by score
        scores = [score for _, score in candidates]
        assert scores == sorted(scores, reverse=True), "Candidates should be sorted by score"

    def test_parking_assignment(self):
        """Test complete parking assignment"""
        vehicle = VehicleInfo(
            plate_number="DL01AB1234",
            latitude=40.7128,
            longitude=-74.0060,
            vehicle_type="car"
        )

        assignment = self.assignment_engine.assign_parking(
            "DL01AB1234",
            vehicle,
            duration_minutes=120
        )

        assert assignment is not None, "Assignment should succeed"
        assert assignment.token_number is not None, "Token should be generated"
        assert assignment.lot_id > 0, "Lot ID should be positive"
        assert assignment.assigned_slot is not None, "Slot should be assigned"
        assert assignment.confidence_score >= 0, "Confidence score should be valid"

    def test_parking_release(self):
        """Test releasing parking assignment"""
        vehicle = VehicleInfo(
            plate_number="DL01AB1234",
            latitude=40.7128,
            longitude=-74.0060,
            vehicle_type="car"
        )

        # Assign parking
        assignment = self.assignment_engine.assign_parking("DL01AB1234", vehicle)
        initial_slots = self.assignment_engine.parking_lots[assignment.lot_id].available_slots

        # Release parking
        success = self.assignment_engine.release_parking("DL01AB1234")
        
        assert success, "Release should succeed"
        assert self.assignment_engine.parking_lots[assignment.lot_id].available_slots == initial_slots + 1

    def test_lot_occupancy_rate(self):
        """Test lot occupancy calculation"""
        status = self.assignment_engine.get_lot_status(1)
        
        assert status is not None
        assert 'occupancy_rate' in status
        assert 0 <= status['occupancy_rate'] <= 100

    # ==================== SMS Service Tests ====================

    def test_sms_service_initialization(self):
        """Test SMS service initializes"""
        assert self.sms_service is not None
        # SMS service should handle missing credentials gracefully
        assert self.sms_service.message_log is not None

    def test_sms_message_formatting(self):
        """Test SMS message formatting"""
        message = self.sms_service._format_assignment_message(
            "DL01AB1234",
            "Central Garage",
            "A1",
            "PKG1AB341704123456",
            11.00,
            0.3
        )

        assert "DL01AB1234" in message
        assert "Central Garage" in message
        assert "PKG1AB341704123456" in message
        assert "$11.00" in message

    def test_sms_message_log(self):
        """Test SMS message logging"""
        # Simulate message log entries
        initial_count = len(self.sms_service.message_log)
        
        # Note: actual SMS won't send without credentials
        stats = self.sms_service.get_message_stats()
        
        assert isinstance(stats, dict)
        assert 'total_messages' in stats

    # ==================== Thermal Printer Tests ====================

    def test_printer_service_initialization(self):
        """Test printer service initializes"""
        assert self.printer_service is not None
        assert self.printer_service.system_printer is not None

    def test_token_image_generation(self):
        """Test parking token image generation"""
        image = self.printer_service._generate_ticket_image(
            "PKG1AB341704123456",
            "DL01AB1234",
            "Central Garage",
            "A1",
            "10:30:00",
            "12:30:00",
            11.00
        )

        assert image is not None
        assert image.width == 384
        assert image.height == 600

    def test_qr_code_generation(self):
        """Test QR code generation"""
        qr_image = self.printer_service._generate_qr_code("PKG1AB341704123456")
        
        assert qr_image is not None
        assert qr_image.size[0] > 0
        assert qr_image.size[1] > 0

    # ==================== End-to-End Integration Tests ====================

    def test_complete_parking_flow(self):
        """Test complete automated parking flow"""
        # 1. Vehicle arrives with license plate
        plate_number = "DL01AB1234"

        # 2. Get vehicle location
        vehicle = VehicleInfo(
            plate_number=plate_number,
            latitude=40.7128,
            longitude=-74.0060,
            vehicle_type="car"
        )

        # 3. Assign parking
        assignment = self.assignment_engine.assign_parking(
            plate_number,
            vehicle,
            duration_minutes=120
        )

        assert assignment is not None, "Parking assignment should succeed"

        # 4. Verify token is valid
        assert len(assignment.token_number) > 0
        assert assignment.lot_id > 0
        assert 0 <= assignment.confidence_score <= 100

        # 5. Generate ticket
        ticket_image = self.printer_service._generate_ticket_image(
            assignment.token_number,
            plate_number,
            assignment.lot_name,
            assignment.assigned_slot,
            datetime.now().strftime("%H:%M:%S"),
            datetime.now().strftime("%H:%M:%S"),
            assignment.estimated_cost
        )

        assert ticket_image is not None

        # 6. Verify assignment is tracked
        tracked = self.assignment_engine.get_assignment(plate_number)
        assert tracked is not None
        assert tracked.token_number == assignment.token_number

        # 7. Release parking
        success = self.assignment_engine.release_parking(plate_number)
        assert success

    def test_multiple_concurrent_assignments(self):
        """Test handling multiple concurrent parking assignments"""
        plates = ["DL01AB1234", "KA51CD5678", "MH03EF9012"]
        assignments = []

        for plate in plates:
            vehicle = VehicleInfo(
                plate_number=plate,
                latitude=40.7128 + len(assignments) * 0.001,
                longitude=-74.0060,
                vehicle_type="car"
            )

            assignment = self.assignment_engine.assign_parking(
                plate,
                vehicle,
                duration_minutes=120
            )

            assert assignment is not None
            assignments.append(assignment)

        # Verify all assignments are independent
        assert len(assignments) == 3
        assert len(set(a.token_number for a in assignments)) == 3

        # Verify all lots still have capacity
        for lot_id in [1, 2, 3]:
            status = self.assignment_engine.get_lot_status(lot_id)
            assert status['available_slots'] >= 0

    def test_error_handling_no_available_lots(self):
        """Test error handling when no lots are available"""
        # Fill up all lots
        for i in range(3):
            for j in range(200):
                self.assignment_engine.parking_lots[i+1].available_slots = 0

        # Try to assign
        vehicle = VehicleInfo(
            plate_number="DL01AB1234",
            latitude=40.7128,
            longitude=-74.0060
        )

        assignment = self.assignment_engine.assign_parking("DL01AB1234", vehicle)
        assert assignment is None, "Should return None when no lots available"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

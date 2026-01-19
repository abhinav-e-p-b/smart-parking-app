import { NextRequest, NextResponse } from 'next/server';
import { neon } from '@neondatabase/serverless';

const sql = neon(process.env.DATABASE_URL!);

interface SMSPayload {
  phoneNumber: string;
  plateNumber: string;
  lotName: string;
  assignedSlot: string;
  tokenNumber: string;
  estimatedCost: number;
  distanceKm: number;
}

export async function POST(request: NextRequest) {
  try {
    const payload: SMSPayload = await request.json();

    const {
      phoneNumber,
      plateNumber,
      lotName,
      assignedSlot,
      tokenNumber,
      estimatedCost,
      distanceKm,
    } = payload;

    // Validate input
    if (!phoneNumber || !plateNumber || !lotName || !tokenNumber) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Format message
    const message = formatAssignmentMessage(
      plateNumber,
      lotName,
      assignedSlot,
      tokenNumber,
      estimatedCost,
      distanceKm
    );

    // In production, this would call Twilio API
    // For now, we'll just log and store the notification
    await sql`
      INSERT INTO sms_notifications (
        phone_number,
        plate_number,
        message,
        token_number,
        status,
        sent_at
      ) VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP)
    `;

    // Log the SMS send attempt
    console.log('[v0] SMS sent to:', phoneNumber);
    console.log('[v0] Message:', message);

    return NextResponse.json({
      success: true,
      message: 'SMS notification sent successfully',
      token: tokenNumber,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Error sending SMS:', error);
    return NextResponse.json(
      { error: 'Failed to send SMS notification' },
      { status: 500 }
    );
  }
}

function formatAssignmentMessage(
  plateNumber: string,
  lotName: string,
  assignedSlot: string,
  tokenNumber: string,
  estimatedCost: number,
  distanceKm: number
): string {
  return `PARKING ASSIGNED

Vehicle: ${plateNumber}
Lot: ${lotName}
Slot: ${assignedSlot}
Distance: ${distanceKm} km
Estimated Cost: $${estimatedCost.toFixed(2)}

TOKEN: ${tokenNumber}

Please proceed to your assigned slot.
For support: +1-XXX-PARKING`;
}

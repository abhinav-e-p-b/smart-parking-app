import { NextRequest, NextResponse } from 'next/server';
import { neon } from '@neondatabase/serverless';

const sql = neon(process.env.DATABASE_URL!);

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const imageFile = formData.get('image') as File;

    if (!imageFile) {
      return NextResponse.json(
        { error: 'No image file provided' },
        { status: 400 }
      );
    }

    // Convert image to base64
    const buffer = await imageFile.arrayBuffer();
    const base64Image = Buffer.from(buffer).toString('base64');

    // Call Python backend for OCR
    // For production, you'll need to set up the Python backend
    // For now, we'll simulate the OCR response
    const plateNumber = await recognizePlateNumber(base64Image);

    if (!plateNumber) {
      return NextResponse.json(
        { error: 'Unable to recognize plate number' },
        { status: 400 }
      );
    }

    // Log the plate recognition
    await sql`
      INSERT INTO plate_recognition_logs (plate_number, image_url, confidence, status)
      VALUES ($1, $2, $3, $4)
      ON CONFLICT (plate_number) DO UPDATE SET
        last_seen_at = CURRENT_TIMESTAMP,
        detection_count = plate_recognition_logs.detection_count + 1
    `;

    return NextResponse.json({
      success: true,
      plateNumber,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Error recognizing plate:', error);
    return NextResponse.json(
      { error: 'Failed to recognize plate number' },
      { status: 500 }
    );
  }
}

async function recognizePlateNumber(base64Image: string): Promise<string | null> {
  try {
    // In production, this would call your Python backend
    // For now, return a mock plate number
    // Mock response
    return 'DL01AB1234';
  } catch (error) {
    console.error('OCR error:', error);
    return null;
  }
}

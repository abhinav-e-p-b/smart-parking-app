import { NextRequest, NextResponse } from 'next/server';
import { neon } from '@neondatabase/serverless';

const sql = neon(process.env.DATABASE_URL!);

interface PrintTokenPayload {
  tokenNumber: string;
  plateNumber: string;
  lotName: string;
  slotNumber: string;
  entryTime: string;
  estimatedExitTime: string;
  estimatedCost: number;
}

export async function POST(request: NextRequest) {
  try {
    const payload: PrintTokenPayload = await request.json();

    const {
      tokenNumber,
      plateNumber,
      lotName,
      slotNumber,
      entryTime,
      estimatedExitTime,
      estimatedCost,
    } = payload;

    // Validate input
    if (!tokenNumber || !plateNumber || !lotName) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Store printer job in database
    await sql`
      INSERT INTO printer_jobs (
        token_number,
        plate_number,
        lot_name,
        slot_number,
        entry_time,
        estimated_exit_time,
        estimated_cost,
        job_type,
        status,
        created_at
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, CURRENT_TIMESTAMP)
    `;

    // In production, this would integrate with thermal printer service
    // For now, we'll simulate the print job
    console.log('[v0] Print job created:', {
      tokenNumber,
      plateNumber,
      lotName,
      slotNumber,
    });

    return NextResponse.json({
      success: true,
      message: 'Print job sent to thermal printer',
      tokenNumber,
      jobId: `PRINT_${tokenNumber}_${Date.now()}`,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Error creating print job:', error);
    return NextResponse.json(
      { error: 'Failed to create print job' },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const tokenNumber = request.nextUrl.searchParams.get('token');

    if (!tokenNumber) {
      return NextResponse.json(
        { error: 'Token number required' },
        { status: 400 }
      );
    }

    // Get print job status
    const jobs = await sql`
      SELECT * FROM printer_jobs
      WHERE token_number = $1
      ORDER BY created_at DESC
      LIMIT 1
    `;

    if (jobs.length === 0) {
      return NextResponse.json(
        { error: 'Print job not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      job: jobs[0],
    });
  } catch (error) {
    console.error('Error getting print job:', error);
    return NextResponse.json(
      { error: 'Failed to retrieve print job status' },
      { status: 500 }
    );
  }
}

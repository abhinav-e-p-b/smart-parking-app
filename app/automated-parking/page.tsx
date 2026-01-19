'use client';

import { useState } from 'react';
import { CameraCapture } from '@/components/camera-capture';
import { ParkingTokenDisplay } from '@/components/parking-token-display';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Loader2, CheckCircle, AlertCircle, Camera } from 'lucide-react';

interface ParkingAssignment {
  tokenNumber: string;
  plateNumber: string;
  lotName: string;
  assignedSlot: string;
  distance_km: number;
  estimated_cost: number;
  duration_minutes: number;
  confidence_score: number;
}

type Stage = 'idle' | 'capturing' | 'recognizing' | 'assigning' | 'success' | 'error';

export default function AutomatedParkingPage() {
  const [stage, setStage] = useState<Stage>('idle');
  const [error, setError] = useState<string | null>(null);
  const [assignment, setAssignment] = useState<ParkingAssignment | null>(null);
  const [plateNumber, setPlateNumber] = useState<string | null>(null);
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handlePlateDetected = async (plate: string, image: string) => {
    setPlateNumber(plate);
    setImageBase64(image);
    setStage('recognizing');
    setError(null);

    // Simulate delay for OCR processing
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Proceed to parking assignment
    await assignParking(plate);
  };

  const assignParking = async (plate: string) => {
    setStage('assigning');
    setIsLoading(true);

    try {
      // Call API to assign parking
      const response = await fetch('/api/predict-availability', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          address: 'Current Location',
          plateNumber: plate,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get parking recommendation');
      }

      const data = await response.json();

      if (data.recommendations && data.recommendations.length > 0) {
        const lot = data.recommendations[0];

        // Create assignment object
        const newAssignment: ParkingAssignment = {
          tokenNumber: generateToken(plate, lot.spot_id),
          plateNumber: plate,
          lotName: lot.name,
          assignedSlot: `${lot.spot_id}-A1`,
          distance_km: lot.distance_km,
          estimated_cost: lot.price_per_hour * 2, // Default 2 hours
          duration_minutes: 120,
          confidence_score: lot.confidence || 85,
        };

        setAssignment(newAssignment);

        // Send SMS notification
        await sendSmsNotification(newAssignment);

        // Send print job to thermal printer
        await sendPrintJob(newAssignment);

        setStage('success');
      } else {
        throw new Error('No parking available');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to assign parking';
      setError(errorMessage);
      setStage('error');
      console.error('Assignment error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const sendSmsNotification = async (assignmentData: ParkingAssignment) => {
    try {
      await fetch('/api/send-parking-sms', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phoneNumber: '+1234567890', // In production, get from user
          plateNumber: assignmentData.plateNumber,
          lotName: assignmentData.lotName,
          assignedSlot: assignmentData.assignedSlot,
          tokenNumber: assignmentData.tokenNumber,
          estimatedCost: assignmentData.estimated_cost,
          distanceKm: assignmentData.distance_km,
        }),
      });
    } catch (err) {
      console.error('SMS sending error:', err);
    }
  };

  const sendPrintJob = async (assignmentData: ParkingAssignment) => {
    try {
      const now = new Date();
      const exitTime = new Date(now.getTime() + assignmentData.duration_minutes * 60000);

      await fetch('/api/print-parking-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tokenNumber: assignmentData.tokenNumber,
          plateNumber: assignmentData.plateNumber,
          lotName: assignmentData.lotName,
          slotNumber: assignmentData.assignedSlot,
          entryTime: now.toLocaleTimeString(),
          estimatedExitTime: exitTime.toLocaleTimeString(),
          estimatedCost: assignmentData.estimated_cost,
        }),
      });
    } catch (err) {
      console.error('Print job error:', err);
    }
  };

  const handleReset = () => {
    setStage('idle');
    setError(null);
    setAssignment(null);
    setPlateNumber(null);
    setImageBase64(null);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Automated Parking System</h1>
          <p className="text-lg text-gray-600">AI-powered parking assignment with instant token generation</p>
        </div>

        {/* Progress Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            {[
              { stage: 'capturing', label: 'Capture' },
              { stage: 'recognizing', label: 'Recognize' },
              { stage: 'assigning', label: 'Assign' },
              { stage: 'success', label: 'Done' },
            ].map((step, idx) => (
              <div key={step.stage} className="flex items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm transition-all ${
                    ['capturing', 'recognizing', 'assigning', 'success'].includes(stage)
                      ? stage === step.stage
                        ? 'bg-blue-600 text-white'
                        : ['idle'].includes(stage)
                        ? 'bg-gray-300 text-gray-600'
                        : 'bg-green-600 text-white'
                      : 'bg-gray-300 text-gray-600'
                  }`}
                >
                  {['capturing', 'recognizing', 'assigning', 'success'].indexOf(stage) >
                  ['capturing', 'recognizing', 'assigning', 'success'].indexOf(step.stage) ? (
                    <CheckCircle className="w-6 h-6" />
                  ) : (
                    idx + 1
                  )}
                </div>
                {idx < 3 && (
                  <div
                    className={`w-16 h-1 mx-2 transition-all ${
                      ['capturing', 'recognizing', 'assigning', 'success'].indexOf(stage) >
                      ['capturing', 'recognizing', 'assigning', 'success'].indexOf(step.stage)
                        ? 'bg-green-600'
                        : 'bg-gray-300'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
          <p className="text-center text-sm text-gray-600 font-semibold uppercase tracking-wide">
            {stage === 'idle' && 'Ready to capture license plate'}
            {stage === 'capturing' && 'Capturing image...'}
            {stage === 'recognizing' && 'Recognizing license plate...'}
            {stage === 'assigning' && 'Finding optimal parking lot...'}
            {stage === 'success' && 'Parking assigned successfully!'}
            {stage === 'error' && 'An error occurred'}
          </p>
        </div>

        {/* Content Area */}
        <div className="space-y-4">
          {/* Idle State */}
          {stage === 'idle' && (
            <Card className="p-8 text-center">
              <div className="mb-6">
                <div className="w-24 h-24 mx-auto bg-blue-100 rounded-full flex items-center justify-center mb-4">
                  <Camera className="w-12 h-12 text-blue-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Ready to Park?</h2>
                <p className="text-gray-600 mb-6">
                  Let our AI system find the perfect parking spot for you in seconds
                </p>
              </div>

              <Button
                onClick={() => setStage('capturing')}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-6 text-lg"
              >
                <Camera className="w-5 h-5 mr-2" />
                Start Plate Recognition
              </Button>

              <p className="text-xs text-gray-500 mt-4">
                We'll scan your license plate and automatically assign the best available parking spot
              </p>
            </Card>
          )}

          {/* Camera Capture */}
          {stage === 'capturing' && (
            <CameraCapture
              onPlateDetected={handlePlateDetected}
              onClose={() => setStage('idle')}
            />
          )}

          {/* Loading States */}
          {(stage === 'recognizing' || stage === 'assigning') && (
            <Card className="p-8">
              <div className="flex flex-col items-center justify-center gap-4">
                <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
                <div className="text-center">
                  <p className="font-semibold text-gray-900 mb-1">
                    {stage === 'recognizing' ? 'Recognizing Plate...' : 'Finding Best Parking Lot...'}
                  </p>
                  <p className="text-sm text-gray-600">
                    {stage === 'recognizing'
                      ? 'Analyzing your license plate image'
                      : `Using AI to find optimal parking for ${plateNumber}`}
                  </p>
                </div>
              </div>
            </Card>
          )}

          {/* Success State */}
          {stage === 'success' && assignment && (
            <div className="space-y-4">
              <ParkingTokenDisplay
                token={{
                  ...assignment,
                  entryTime: new Date().toLocaleTimeString(),
                  estimatedExitTime: new Date(
                    Date.now() + assignment.duration_minutes * 60000
                  ).toLocaleTimeString(),
                }}
                onPrint={async () => {
                  try {
                    await sendPrintJob(assignment);
                    alert('Print job sent to thermal printer!');
                  } catch (err) {
                    alert('Failed to send print job');
                  }
                }}
              />

              <Button
                onClick={handleReset}
                variant="outline"
                className="w-full bg-transparent"
              >
                Scan Another Vehicle
              </Button>
            </div>
          )}

          {/* Error State */}
          {stage === 'error' && (
            <Card className="p-6 border-red-200 bg-red-50">
              <div className="flex gap-4">
                <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h3 className="font-semibold text-red-900 mb-1">Parking Assignment Failed</h3>
                  <p className="text-red-700 text-sm mb-4">{error}</p>
                  <div className="flex gap-2">
                    <Button
                      onClick={() => setStage('capturing')}
                      className="bg-red-600 hover:bg-red-700"
                    >
                      Try Again
                    </Button>
                    <Button onClick={handleReset} variant="outline">
                      Start Over
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          )}
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
          <Card className="p-4">
            <h3 className="font-semibold text-gray-900 mb-2">AI Recognition</h3>
            <p className="text-sm text-gray-600">
              Powered by EasyOCR for accurate license plate detection
            </p>
          </Card>
          <Card className="p-4">
            <h3 className="font-semibold text-gray-900 mb-2">Smart Assignment</h3>
            <p className="text-sm text-gray-600">
              ML-based optimization for best parking spot selection
            </p>
          </Card>
          <Card className="p-4">
            <h3 className="font-semibold text-gray-900 mb-2">Instant Printing</h3>
            <p className="text-sm text-gray-600">
              Thermal printer support for on-site ticket generation
            </p>
          </Card>
        </div>
      </div>
    </main>
  );
}

function generateToken(plateNumber: string, lotId: number): string {
  const timestamp = Date.now().toString(36).toUpperCase();
  const plate = plateNumber.slice(-4).toUpperCase();
  return `PKG${lotId}${plate}${timestamp}`;
}

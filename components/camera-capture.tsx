'use client';

import React from "react"

import { useRef, useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Camera, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

interface CameraCaptureProps {
  onPlateDetected: (plateNumber: string, imageBase64: string) => void;
  onClose?: () => void;
}

export function CameraCapture({ onPlateDetected, onClose }: CameraCaptureProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [isCameraActive, setIsCameraActive] = useState(false);
  const [detectedPlate, setDetectedPlate] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [cameraPermission, setCameraPermission] = useState<'granted' | 'denied' | 'pending'>('pending');

  // Initialize camera
  useEffect(() => {
    const initCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: 'environment',
            width: { ideal: 1280 },
            height: { ideal: 720 },
          },
        });

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setIsCameraActive(true);
          setCameraPermission('granted');
        }
      } catch (err) {
        console.error('Camera access denied:', err);
        setError('Camera access denied. Please enable camera permissions.');
        setCameraPermission('denied');
      }
    };

    initCamera();

    return () => {
      // Cleanup camera stream
      if (videoRef.current?.srcObject) {
        const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
        tracks.forEach(track => track.stop());
      }
    };
  }, []);

  // Capture frame from video
  const captureFrame = () => {
    if (videoRef.current && canvasRef.current) {
      const context = canvasRef.current.getContext('2d');
      if (context) {
        canvasRef.current.width = videoRef.current.videoWidth;
        canvasRef.current.height = videoRef.current.videoHeight;
        context.drawImage(videoRef.current, 0, 0);
        const imageBase64 = canvasRef.current.toDataURL('image/jpeg', 0.9);
        setCapturedImage(imageBase64);
        recognizePlate(imageBase64);
      }
    }
  };

  // Send image to OCR API
  const recognizePlate = async (imageBase64: string) => {
    setIsLoading(true);
    setError(null);
    setDetectedPlate(null);

    try {
      // Convert base64 to blob
      const response = await fetch(imageBase64);
      const blob = await response.blob();

      const formData = new FormData();
      formData.append('image', blob, 'plate.jpg');

      const apiResponse = await fetch('/api/recognize-plate', {
        method: 'POST',
        body: formData,
      });

      if (!apiResponse.ok) {
        throw new Error('Failed to recognize plate');
      }

      const data = await apiResponse.json();

      if (data.plateNumber) {
        setDetectedPlate(data.plateNumber);
        // Call the callback after detection
        setTimeout(() => {
          onPlateDetected(data.plateNumber, imageBase64);
        }, 500);
      } else {
        setError('No license plate detected. Please try again.');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to recognize plate';
      setError(errorMessage);
      console.error('OCR error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle file upload
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const imageBase64 = e.target?.result as string;
        setCapturedImage(imageBase64);
        recognizePlate(imageBase64);
      };
      reader.readAsDataURL(file);
    }
  };

  // Retry capture
  const handleRetry = () => {
    setDetectedPlate(null);
    setCapturedImage(null);
    setError(null);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl bg-white">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Camera className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-semibold">License Plate Scanner</h2>
            </div>
            {onClose && (
              <button
                onClick={onClose}
                className="p-1 hover:bg-gray-100 rounded-lg transition"
              >
                <X className="w-5 h-5 text-gray-600" />
              </button>
            )}
          </div>

          {/* Camera/Image Display */}
          <div className="mb-4 bg-gray-900 rounded-lg overflow-hidden aspect-video flex items-center justify-center">
            {capturedImage ? (
              <img
                src={capturedImage || "/placeholder.svg"}
                alt="Captured plate"
                className="w-full h-full object-cover"
              />
            ) : isCameraActive ? (
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="flex flex-col items-center gap-2 text-gray-400">
                <Camera className="w-12 h-12" />
                <p>Camera not available</p>
              </div>
            )}
          </div>

          {/* Status Messages */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex gap-2">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-red-900">Recognition Failed</p>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          )}

          {detectedPlate && (
            <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <p className="font-semibold text-green-900">Plate Recognized!</p>
              </div>
              <div className="mt-3 p-3 bg-white border-2 border-green-300 rounded-lg font-mono text-lg font-bold text-center text-gray-900">
                {detectedPlate}
              </div>
            </div>
          )}

          {isLoading && (
            <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg flex items-center gap-2">
              <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
              <p className="text-blue-900">Analyzing plate...</p>
            </div>
          )}

          {/* Hidden Canvas for capture */}
          <canvas ref={canvasRef} className="hidden" />

          {/* Hidden File Input */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileUpload}
            className="hidden"
          />

          {/* Buttons */}
          <div className="flex gap-3 flex-wrap">
            {!capturedImage ? (
              <>
                <Button
                  onClick={captureFrame}
                  disabled={!isCameraActive || isLoading}
                  className="flex-1 bg-blue-600 hover:bg-blue-700"
                >
                  <Camera className="w-4 h-4 mr-2" />
                  Capture Photo
                </Button>
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  variant="outline"
                  className="flex-1"
                >
                  Upload Image
                </Button>
              </>
            ) : (
              <>
                <Button
                  onClick={handleRetry}
                  variant="outline"
                  className="flex-1 bg-transparent"
                >
                  Try Again
                </Button>
                {detectedPlate && (
                  <Button
                    onClick={() => onPlateDetected(detectedPlate, capturedImage)}
                    className="flex-1 bg-green-600 hover:bg-green-700"
                  >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Confirm & Proceed
                  </Button>
                )}
              </>
            )}

            {onClose && (
              <Button
                onClick={onClose}
                variant="outline"
                className="flex-1 bg-transparent"
              >
                Close
              </Button>
            )}
          </div>

          {/* Info */}
          <p className="text-xs text-gray-500 mt-4 text-center">
            Position your vehicle's license plate clearly in the frame and tap Capture Photo
          </p>
        </div>
      </Card>
    </div>
  );
}

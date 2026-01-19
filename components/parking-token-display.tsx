'use client';

import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Printer, Download, Share2, Copy, CheckCircle } from 'lucide-react';
import { useState } from 'react';

interface ParkingTokenDisplayProps {
  token: {
    tokenNumber: string;
    plateNumber: string;
    lotName: string;
    assignedSlot: string;
    distance_km: number;
    estimated_cost: number;
    duration_minutes: number;
    confidence_score: number;
    entryTime?: string;
    estimatedExitTime?: string;
  };
  onPrint?: () => void;
  onDownload?: () => void;
}

export function ParkingTokenDisplay({ token, onPrint, onDownload }: ParkingTokenDisplayProps) {
  const [copied, setCopied] = useState(false);
  const [isPrinting, setIsPrinting] = useState(false);

  const handleCopyToken = () => {
    navigator.clipboard.writeText(token.tokenNumber);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handlePrint = async () => {
    setIsPrinting(true);
    try {
      if (onPrint) {
        await onPrint();
      } else {
        // Default print action
        window.print();
      }
    } catch (error) {
      console.error('Print error:', error);
    } finally {
      setIsPrinting(false);
    }
  };

  const hours = token.duration_minutes / 60;
  const entryTime = token.entryTime || new Date().toLocaleTimeString();
  const exitTime = token.estimatedExitTime || 
    new Date(Date.now() + token.duration_minutes * 60000).toLocaleTimeString();

  return (
    <div className="space-y-4">
      {/* Main Token Card */}
      <Card className="border-2 border-green-200 bg-gradient-to-br from-green-50 to-emerald-50 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white p-4">
          <h2 className="text-2xl font-bold text-center">PARKING CONFIRMED</h2>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Token Number */}
          <div className="bg-white border-2 border-green-300 rounded-lg p-4 text-center">
            <p className="text-gray-600 text-sm font-semibold uppercase tracking-wide mb-2">
              Your Parking Token
            </p>
            <p className="font-mono text-3xl font-bold text-gray-900 break-words">
              {token.tokenNumber}
            </p>
            <div className="flex justify-center gap-2 mt-3">
              <Button
                size="sm"
                variant="outline"
                onClick={handleCopyToken}
                className="text-xs bg-transparent"
              >
                {copied ? (
                  <>
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3 mr-1" />
                    Copy
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Vehicle & Parking Info Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white p-3 rounded-lg border border-gray-200">
              <p className="text-gray-600 text-xs font-semibold uppercase mb-1">
                License Plate
              </p>
              <p className="text-lg font-bold text-gray-900">
                {token.plateNumber}
              </p>
            </div>

            <div className="bg-white p-3 rounded-lg border border-gray-200">
              <p className="text-gray-600 text-xs font-semibold uppercase mb-1">
                Assigned Slot
              </p>
              <p className="text-lg font-bold text-gray-900">
                {token.assignedSlot}
              </p>
            </div>

            <div className="bg-white p-3 rounded-lg border border-gray-200">
              <p className="text-gray-600 text-xs font-semibold uppercase mb-1">
                Parking Lot
              </p>
              <p className="text-sm font-semibold text-gray-900">
                {token.lotName}
              </p>
            </div>

            <div className="bg-white p-3 rounded-lg border border-gray-200">
              <p className="text-gray-600 text-xs font-semibold uppercase mb-1">
                Distance
              </p>
              <p className="text-lg font-bold text-gray-900">
                {token.distance_km} km
              </p>
            </div>
          </div>

          {/* Time & Cost Info */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
              <p className="text-blue-600 text-xs font-semibold uppercase mb-2">
                Entry Time
              </p>
              <p className="text-base font-semibold text-blue-900">
                {entryTime}
              </p>
            </div>

            <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
              <p className="text-orange-600 text-xs font-semibold uppercase mb-2">
                Estimated Exit
              </p>
              <p className="text-base font-semibold text-orange-900">
                {exitTime}
              </p>
            </div>

            <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
              <p className="text-purple-600 text-xs font-semibold uppercase mb-2">
                Duration
              </p>
              <p className="text-base font-semibold text-purple-900">
                {hours.toFixed(1)} hours
              </p>
            </div>

            <div className="bg-red-50 p-4 rounded-lg border border-red-200">
              <p className="text-red-600 text-xs font-semibold uppercase mb-2">
                Estimated Cost
              </p>
              <p className="text-base font-semibold text-red-900">
                ${token.estimated_cost.toFixed(2)}
              </p>
            </div>
          </div>

          {/* Confidence Score */}
          <div className="bg-indigo-50 p-4 rounded-lg border border-indigo-200">
            <p className="text-indigo-600 text-xs font-semibold uppercase mb-2">
              AI Confidence Score
            </p>
            <div className="flex items-end gap-3">
              <div className="flex-1">
                <div className="w-full bg-indigo-200 rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-indigo-600 h-full transition-all duration-300"
                    style={{ width: `${token.confidence_score}%` }}
                  />
                </div>
              </div>
              <p className="text-lg font-bold text-indigo-900">
                {token.confidence_score.toFixed(1)}%
              </p>
            </div>
          </div>

          {/* Important Note */}
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
            <p className="text-yellow-800 text-sm">
              <strong>Important:</strong> Keep this token safe. You'll need it to retrieve your vehicle. 
              Present it at the exit gate to ensure smooth vehicle retrieval.
            </p>
          </div>
        </div>
      </Card>

      {/* Action Buttons */}
      <div className="flex gap-3 flex-wrap">
        <Button
          onClick={handlePrint}
          disabled={isPrinting}
          className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
        >
          <Printer className="w-4 h-4 mr-2" />
          {isPrinting ? 'Printing...' : 'Print Token'}
        </Button>

        {onDownload && (
          <Button
            onClick={onDownload}
            variant="outline"
            className="flex-1 bg-transparent"
          >
            <Download className="w-4 h-4 mr-2" />
            Download
          </Button>
        )}

        <Button
          onClick={() => {
            // Generate share message
            const message = `I'm parked at ${token.lotName}, Slot ${token.assignedSlot}. Token: ${token.tokenNumber}`;
            if (navigator.share) {
              navigator.share({
                title: 'Parking Token',
                text: message,
              }).catch(console.error);
            } else {
              navigator.clipboard.writeText(message);
              alert('Copied to clipboard!');
            }
          }}
          variant="outline"
          className="flex-1"
        >
          <Share2 className="w-4 h-4 mr-2" />
          Share
        </Button>
      </div>

      {/* Digital Copy */}
      <Card className="p-4 bg-gray-50">
        <p className="text-xs text-gray-600 mb-2 font-semibold">DIGITAL COPY</p>
        <div className="bg-white p-3 rounded border border-gray-300 font-mono text-xs overflow-auto">
          <p className="font-bold mb-1">PARKING TICKET</p>
          <p>Token: {token.tokenNumber}</p>
          <p>Plate: {token.plateNumber}</p>
          <p>Lot: {token.lotName}</p>
          <p>Slot: {token.assignedSlot}</p>
          <p>Entry: {entryTime}</p>
          <p>Exit: {exitTime}</p>
          <p>Cost: ${token.estimated_cost.toFixed(2)}</p>
        </div>
      </Card>
    </div>
  );
}

"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { AlertCircle } from "lucide-react"

interface ParkingDetailsModalProps {
  spot: {
    spot_id: number
    name: string
    latitude: number
    longitude: number
    availability_probability: number
    distance_km: number
    traffic_level: string
    price_per_hour: number
    available_slots: number
    total_slots: number
    confidence: number
    scores: {
      availability: number
      distance: number
      traffic: number
      price: number
      final: number
    }
  }
  onBook: (spotId: number) => void
  onClose: () => void
}

export function ParkingDetailsModal({ spot, onBook, onClose }: ParkingDetailsModalProps) {
  const [bookingLoading, setBookingLoading] = useState(false)

  const handleBook = async () => {
    setBookingLoading(true)
    try {
      const token = localStorage.getItem("auth_token")
      if (!token) {
        alert("Please sign in to make a booking")
        return
      }

      const response = await fetch("/api/bookings", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          parking_slot_id: spot.spot_id,
          check_in_time: new Date().toISOString(),
        }),
      })

      if (!response.ok) throw new Error("Booking failed")
      onBook(spot.spot_id)
      onClose()
    } catch (error) {
      alert("Failed to book parking spot")
    } finally {
      setBookingLoading(false)
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 75) return "bg-green-100 text-green-800"
    if (confidence >= 50) return "bg-yellow-100 text-yellow-800"
    return "bg-red-100 text-red-800"
  }

  const getTrafficColor = (level: string) => {
    switch (level) {
      case "Low":
        return "bg-green-100 text-green-800"
      case "Medium":
        return "bg-yellow-100 text-yellow-800"
      case "High":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>{spot.name}</CardTitle>
          <CardDescription>{spot.distance_km} km away</CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Availability Section */}
          <div className="bg-blue-50 p-4 rounded-lg space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-700">Availability Probability</span>
              <Badge className={getConfidenceColor(spot.confidence)}>{spot.confidence}%</Badge>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-2">
              <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${spot.confidence}%` }} />
            </div>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-slate-600 uppercase tracking-wide">Available Slots</p>
              <p className="text-2xl font-bold text-slate-900">
                {spot.available_slots}/{spot.total_slots}
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-600 uppercase tracking-wide">Price/Hour</p>
              <p className="text-2xl font-bold text-slate-900">${spot.price_per_hour.toFixed(2)}</p>
            </div>
          </div>

          {/* Traffic & Conditions */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-slate-700">Traffic Level:</span>
              <Badge className={getTrafficColor(spot.traffic_level)}>{spot.traffic_level}</Badge>
            </div>
          </div>

          {/* Recommendation Breakdown */}
          <div className="bg-slate-50 p-3 rounded-lg space-y-2 text-sm">
            <p className="font-semibold text-slate-900">Recommendation Score</p>
            <div className="space-y-1">
              <div className="flex justify-between">
                <span>Availability</span>
                <span className="font-medium">{(spot.scores.availability * 100).toFixed(0)}%</span>
              </div>
              <div className="flex justify-between">
                <span>Distance</span>
                <span className="font-medium">{(spot.scores.distance * 100).toFixed(0)}%</span>
              </div>
              <div className="flex justify-between">
                <span>Traffic</span>
                <span className="font-medium">{(spot.scores.traffic * 100).toFixed(0)}%</span>
              </div>
              <div className="flex justify-between">
                <span>Price</span>
                <span className="font-medium">{(spot.scores.price * 100).toFixed(0)}%</span>
              </div>
              <div className="border-t pt-1 flex justify-between font-bold">
                <span>Overall Score</span>
                <span>{(spot.scores.final * 100).toFixed(1)}/100</span>
              </div>
            </div>
          </div>

          {/* Warning if low confidence */}
          {spot.confidence < 50 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 flex gap-2">
              <AlertCircle className="w-4 h-4 text-yellow-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-yellow-700">Low availability confidence. Availability may change quickly.</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2 pt-2">
            <Button onClick={handleBook} disabled={bookingLoading} className="flex-1 bg-blue-600 hover:bg-blue-700">
              {bookingLoading ? "Booking..." : "Book Spot"}
            </Button>
            <Button onClick={onClose} variant="outline" className="flex-1 bg-transparent">
              Close
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

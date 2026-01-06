"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

interface ParkingSpot {
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

interface ParkingRecommendationsProps {
  recommendations: ParkingSpot[]
  onSelectParking: (spot: ParkingSpot) => void
}

export function ParkingRecommendations({ recommendations, onSelectParking }: ParkingRecommendationsProps) {
  if (recommendations.length === 0) {
    return null
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

  const getAvailabilityColor = (prob: number) => {
    if (prob >= 0.7) return "text-green-600"
    if (prob >= 0.4) return "text-yellow-600"
    return "text-red-600"
  }

  return (
    <div className="mt-6 space-y-4">
      <h2 className="text-xl font-bold text-slate-900">Recommendations</h2>

      {recommendations.map((spot, index) => (
        <Card key={spot.spot_id} className={index === 0 ? "border-2 border-blue-500" : ""}>
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <CardTitle className="text-lg">{spot.name}</CardTitle>
                  {index === 0 && <Badge className="bg-blue-600">Best Match</Badge>}
                </div>
                <CardDescription className="mt-1">{spot.distance_km} km away</CardDescription>
              </div>
              <div className={`text-2xl font-bold ${getAvailabilityColor(spot.availability_probability)}`}>
                {spot.confidence}%
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <p className="text-sm text-slate-600">Available Slots</p>
                <p className="text-lg font-semibold">
                  {spot.available_slots}/{spot.total_slots}
                </p>
              </div>
              <div>
                <p className="text-sm text-slate-600">Price/Hour</p>
                <p className="text-lg font-semibold">${spot.price_per_hour.toFixed(2)}</p>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <Badge className={getTrafficColor(spot.traffic_level)}>{spot.traffic_level} Traffic</Badge>
              <span className="text-sm text-slate-600">Score: {(spot.scores.final * 100).toFixed(1)}/100</span>
            </div>

            <Button onClick={() => onSelectParking(spot)} className="w-full bg-blue-600 hover:bg-blue-700">
              View on Map
            </Button>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

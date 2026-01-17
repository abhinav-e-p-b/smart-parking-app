"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { MapPin, TrendingUp, DollarSign, Car, Navigation, Award } from "lucide-react"

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
        return "bg-green-100 text-green-800 border-green-200"
      case "Medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-200"
      case "High":
        return "bg-red-100 text-red-800 border-red-200"
      default:
        return "bg-gray-100 text-gray-800 border-gray-200"
    }
  }

  const getAvailabilityColor = (prob: number) => {
    if (prob >= 0.7) return "text-green-600"
    if (prob >= 0.4) return "text-yellow-600"
    return "text-red-600"
  }

  return (
    <div className="mt-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-900">Top Recommendations</h2>
        <span className="text-sm text-slate-500">{recommendations.length} spots found</span>
      </div>

      {recommendations.map((spot, index) => (
        <Card 
          key={spot.spot_id} 
          className={`transition-all hover:shadow-lg ${
            index === 0 ? "border-2 border-blue-500 bg-blue-50/30" : "border border-slate-200"
          }`}
        >
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <CardTitle className="text-lg">{spot.name}</CardTitle>
                  {index === 0 && (
                    <Badge className="bg-blue-600 text-white border-0">
                      <Award className="w-3 h-3 mr-1" />
                      Best Match
                    </Badge>
                  )}
                </div>
                <CardDescription className="flex items-center gap-1 mt-1">
                  <Navigation className="w-3 h-3" />
                  {spot.distance_km} km away
                </CardDescription>
              </div>
              <div className="text-right">
                <div className={`text-3xl font-bold ${getAvailabilityColor(spot.availability_probability)}`}>
                  {spot.confidence}%
                </div>
                <div className="text-xs text-slate-500">confidence</div>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-4">
            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
                <div className="flex items-center gap-2 mb-1">
                  <Car className="w-4 h-4 text-slate-600" />
                  <p className="text-xs text-slate-600 font-medium">Available</p>
                </div>
                <p className="text-lg font-bold text-slate-900">
                  {spot.available_slots}<span className="text-sm text-slate-500">/{spot.total_slots}</span>
                </p>
              </div>
              <div className="bg-slate-50 rounded-lg p-3 border border-slate-200">
                <div className="flex items-center gap-2 mb-1">
                  <DollarSign className="w-4 h-4 text-slate-600" />
                  <p className="text-xs text-slate-600 font-medium">Price/Hour</p>
                </div>
                <p className="text-lg font-bold text-slate-900">${spot.price_per_hour.toFixed(2)}</p>
              </div>
            </div>

            {/* Traffic Badge & Score */}
            <div className="flex items-center justify-between">
              <Badge className={`border ${getTrafficColor(spot.traffic_level)}`}>
                <TrendingUp className="w-3 h-3 mr-1" />
                {spot.traffic_level} Traffic
              </Badge>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500">Match Score:</span>
                <span className="text-sm font-bold text-blue-600">{(spot.scores.final * 100).toFixed(1)}/100</span>
              </div>
            </div>

            {/* Action Button */}
            <Button 
              onClick={() => onSelectParking(spot)} 
              className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold shadow-md hover:shadow-lg transition-all"
            >
              <MapPin className="w-4 h-4 mr-2" />
              View on Map
            </Button>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
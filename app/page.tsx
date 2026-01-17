"use client"

import { useState } from "react"
import { MapComponent } from "@/components/map-view"
import { ParkingSearchForm } from "@/components/parking-search-form"
import { ParkingRecommendations } from "@/components/parking-recommendations"
import { Header } from "@/components/header"
import { Sparkles, Zap, Shield, Clock } from "lucide-react"

export default function Home() {
  const [selectedLocation, setSelectedLocation] = useState<{
    lat: number
    lng: number
    address?: string
  } | null>(null)
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async (address: string) => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch("/api/predict-availability", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ address }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()
      setRecommendations(data.recommendations || [])
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Failed to fetch recommendations"
      console.error("Error fetching recommendations:", error)
      setError(errorMessage)
      setRecommendations([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-slate-100">
      <Header />

      {/* Hero Section */}
      {recommendations.length === 0 && (
        <div className="container mx-auto px-4 pt-12 pb-8">
          <div className="text-center max-w-3xl mx-auto mb-8">
            <div className="inline-flex items-center gap-2 bg-blue-100 text-blue-700 px-4 py-2 rounded-full text-sm font-medium mb-6">
              <Sparkles className="w-4 h-4" />
              AI-Powered Parking Intelligence
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
              Find Your Perfect{" "}
              <span className="bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
                Parking Spot
              </span>
            </h2>
            <p className="text-lg text-slate-600 mb-8">
              Save time and hassle with our machine learning predictions. Get real-time availability,
              smart recommendations, and instant booking.
            </p>

            {/* Feature Pills */}
            <div className="flex flex-wrap justify-center gap-4 mb-8">
              <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-full shadow-sm border border-slate-200">
                <Zap className="w-4 h-4 text-blue-600" />
                <span className="text-sm font-medium text-slate-700">Instant Results</span>
              </div>
              <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-full shadow-sm border border-slate-200">
                <Shield className="w-4 h-4 text-green-600" />
                <span className="text-sm font-medium text-slate-700">85%+ Accuracy</span>
              </div>
              <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-full shadow-sm border border-slate-200">
                <Clock className="w-4 h-4 text-purple-600" />
                <span className="text-sm font-medium text-slate-700">Save Time</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="container mx-auto px-4 pb-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left sidebar with search */}
          <div className="lg:col-span-1">
            <ParkingSearchForm onSearch={handleSearch} loading={loading} />

            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl shadow-sm">
                <p className="text-red-700 font-medium text-sm">Error</p>
                <p className="text-red-600 text-sm mt-1">{error}</p>
              </div>
            )}

            {recommendations.length > 0 && (
              <ParkingRecommendations
                recommendations={recommendations}
                onSelectParking={(spot) =>
                  setSelectedLocation({
                    lat: spot.latitude,
                    lng: spot.longitude,
                    address: spot.name,
                  })
                }
              />
            )}
          </div>

          {/* Map */}
          <div className="lg:col-span-2">
            <MapComponent selectedLocation={selectedLocation} parkingSpots={recommendations} />
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t bg-white mt-12">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">SP</span>
              </div>
              <span className="text-slate-600 text-sm">
                © 2025 SmartPark. All rights reserved.
              </span>
            </div>
            <div className="flex gap-6 text-sm text-slate-600">
              <a href="#" className="hover:text-blue-600 transition-colors">Privacy</a>
              <a href="#" className="hover:text-blue-600 transition-colors">Terms</a>
              <a href="#" className="hover:text-blue-600 transition-colors">Contact</a>
            </div>
          </div>
        </div>
      </footer>
    </main>
  )
}
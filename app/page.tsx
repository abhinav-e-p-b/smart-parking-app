"use client"

import { useState } from "react"
import { MapComponent } from "@/components/map-view"
import { ParkingSearchForm } from "@/components/parking-search-form"
import { ParkingRecommendations } from "@/components/parking-recommendations"
import { Header } from "@/components/header"

export default function Home() {
  const [searchActive, setSearchActive] = useState(false)
  const [selectedLocation, setSelectedLocation] = useState<{
    lat: number
    lng: number
    address?: string
  } | null>(null)
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)

  const handleSearch = async (address: string) => {
    setLoading(true)
    try {
      // Call backend API to get recommendations
      const response = await fetch("/api/predict-availability", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ address }),
      })
      const data = await response.json()
      setRecommendations(data.recommendations || [])
    } catch (error) {
      console.error("Error fetching recommendations:", error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Header />

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left sidebar with search */}
          <div className="lg:col-span-1">
            <ParkingSearchForm onSearch={handleSearch} loading={loading} />
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
    </main>
  )
}

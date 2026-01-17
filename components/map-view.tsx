"use client"

import { useEffect, useRef } from "react"
import { MapPin, Layers, Navigation2 } from "lucide-react"

interface ParkingSpot {
  spot_id: number
  name: string
  latitude: number
  longitude: number
  availability_probability: number
  distance_km: number
}

interface MapComponentProps {
  selectedLocation: {
    lat: number
    lng: number
    address?: string
  } | null
  parkingSpots: ParkingSpot[]
}

export function MapComponent({ selectedLocation, parkingSpots }: MapComponentProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<any>(null)

  useEffect(() => {
    // Initialize map (placeholder - would integrate Google Maps or Leaflet)
    if (mapContainerRef.current && !mapRef.current) {
      // Map initialization code here
    }
  }, [])

  return (
    <div
      ref={mapContainerRef}
      className="w-full h-[600px] bg-gradient-to-br from-slate-100 to-slate-200 rounded-xl shadow-lg flex items-center justify-center border-2 border-slate-300 relative overflow-hidden"
    >
      {/* Decorative grid pattern */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute inset-0" style={{
          backgroundImage: 'linear-gradient(to right, #cbd5e1 1px, transparent 1px), linear-gradient(to bottom, #cbd5e1 1px, transparent 1px)',
          backgroundSize: '40px 40px'
        }} />
      </div>

      <div className="relative text-center z-10 max-w-md px-6">
        {/* Icon */}
        <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl shadow-lg mb-6">
          <Layers className="w-10 h-10 text-white" />
        </div>

        {/* Content */}
        <h3 className="text-2xl font-bold text-slate-800 mb-3">Interactive Map View</h3>
        
        {selectedLocation ? (
          <div className="space-y-3">
            <div className="bg-white/80 backdrop-blur-sm rounded-lg p-4 shadow-md border border-slate-300">
              <div className="flex items-center justify-center gap-2 text-blue-700 mb-2">
                <MapPin className="w-5 h-5" />
                <span className="font-semibold">Selected Location</span>
              </div>
              <p className="text-slate-700 font-medium">{selectedLocation.address || "Custom location"}</p>
              <p className="text-sm text-slate-500 mt-1">
                Lat: {selectedLocation.lat.toFixed(4)}, Lng: {selectedLocation.lng.toFixed(4)}
              </p>
            </div>
            <p className="text-slate-600 text-sm">
              📍 {parkingSpots.length} parking spot{parkingSpots.length !== 1 ? 's' : ''} nearby
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-slate-600 mb-4">
              Search for a location to see nearby parking options on an interactive map
            </p>
            <div className="flex flex-col gap-2 text-sm text-slate-500">
              <div className="flex items-center justify-center gap-2">
                <Navigation2 className="w-4 h-4 text-blue-600" />
                <span>Real-time navigation</span>
              </div>
              <div className="flex items-center justify-center gap-2">
                <MapPin className="w-4 h-4 text-blue-600" />
                <span>Interactive markers</span>
              </div>
              <div className="flex items-center justify-center gap-2">
                <Layers className="w-4 h-4 text-blue-600" />
                <span>Multiple map layers</span>
              </div>
            </div>
          </div>
        )}

        {/* Integration Note */}
        <div className="mt-6 pt-6 border-t border-slate-300">
          <p className="text-xs text-slate-500">
            🗺️ Integrate with Google Maps or Leaflet for full functionality
          </p>
        </div>
      </div>
    </div>
  )
}
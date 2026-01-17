"use client"

import type React from "react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search, MapPin, Navigation, Sparkles } from "lucide-react"

interface ParkingSearchFormProps {
  onSearch: (address: string) => void
  loading: boolean
}

export function ParkingSearchForm({ onSearch, loading }: ParkingSearchFormProps) {
  const [address, setAddress] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (address.trim()) {
      onSearch(address)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 border border-slate-200">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-gradient-to-br from-blue-100 to-blue-200 rounded-lg flex items-center justify-center">
          <Search className="w-5 h-5 text-blue-700" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-slate-900">Find Parking</h2>
          <p className="text-xs text-slate-500">AI-powered predictions</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <label htmlFor="address" className="block text-sm font-medium text-slate-700 mb-2">
            Where are you going?
          </label>
          <div className="relative">
            <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <Input
              id="address"
              type="text"
              placeholder="Enter destination address..."
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              disabled={loading}
              className="pl-11 h-12 border-slate-300 focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
        </div>

        <Button 
          type="submit" 
          disabled={loading || !address.trim()} 
          className="w-full h-12 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold shadow-md hover:shadow-lg transition-all"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
              Searching...
            </>
          ) : (
            <>
              <Search className="w-5 h-5 mr-2" />
              Find Available Spots
            </>
          )}
        </Button>
      </form>

      <div className="mt-6 pt-6 border-t border-slate-200">
        <div className="flex items-start gap-2 mb-3">
          <Sparkles className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-slate-900 text-sm mb-1">How it works</h3>
            <p className="text-xs text-slate-600">Our AI analyzes real-time data to predict parking availability</p>
          </div>
        </div>
        
        <ul className="space-y-2">
          <li className="flex items-start gap-3 text-sm text-slate-600">
            <span className="flex items-center justify-center w-6 h-6 bg-blue-100 text-blue-700 rounded-full font-bold text-xs flex-shrink-0">1</span>
            <span>Enter your destination</span>
          </li>
          <li className="flex items-start gap-3 text-sm text-slate-600">
            <span className="flex items-center justify-center w-6 h-6 bg-blue-100 text-blue-700 rounded-full font-bold text-xs flex-shrink-0">2</span>
            <span>AI predicts availability in real-time</span>
          </li>
          <li className="flex items-start gap-3 text-sm text-slate-600">
            <span className="flex items-center justify-center w-6 h-6 bg-blue-100 text-blue-700 rounded-full font-bold text-xs flex-shrink-0">3</span>
            <span>View ranked recommendations</span>
          </li>
          <li className="flex items-start gap-3 text-sm text-slate-600">
            <span className="flex items-center justify-center w-6 h-6 bg-blue-100 text-blue-700 rounded-full font-bold text-xs flex-shrink-0">4</span>
            <span>Book and navigate to your spot</span>
          </li>
        </ul>
      </div>
    </div>
  )
}
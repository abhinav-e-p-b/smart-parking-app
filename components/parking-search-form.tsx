"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

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
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold text-slate-900 mb-4">Find Parking</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="address" className="block text-sm font-medium text-slate-700 mb-2">
            Destination Address
          </label>
          <Input
            id="address"
            type="text"
            placeholder="Enter destination address or location"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            disabled={loading}
            className="w-full"
          />
        </div>

        <Button type="submit" disabled={loading || !address.trim()} className="w-full">
          {loading ? "Searching..." : "Search Nearby Parking"}
        </Button>
      </form>

      <div className="mt-6 pt-6 border-t">
        <h3 className="font-semibold text-slate-900 mb-3">How it works:</h3>
        <ul className="space-y-2 text-sm text-slate-600">
          <li className="flex items-start gap-2">
            <span className="font-bold text-blue-600">1.</span>
            <span>Enter your destination address</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="font-bold text-blue-600">2.</span>
            <span>AI predicts parking availability</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="font-bold text-blue-600">3.</span>
            <span>View ranked recommendations</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="font-bold text-blue-600">4.</span>
            <span>Book your preferred spot</span>
          </li>
        </ul>
      </div>
    </div>
  )
}

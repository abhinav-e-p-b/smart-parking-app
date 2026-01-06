"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface BookingDetailsProps {
  booking: {
    id: number
    spotName: string
    spotAddress: string
    checkInTime: string
    duration?: number
    amount?: number
  }
  onCheckout: () => void
}

export function BookingDetails({ booking, onCheckout }: BookingDetailsProps) {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState("")

  const handleCheckout = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem("auth_token")
      const response = await fetch(`/api/bookings/${booking.id}/checkout`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (!response.ok) throw new Error("Checkout failed")

      const data = await response.json()
      setMessage(`Successfully checked out. Amount: $${data.amount_paid.toFixed(2)}`)
      onCheckout()
    } catch (error) {
      setMessage("Checkout failed. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const checkInTime = new Date(booking.checkInTime)
  const currentTime = new Date()
  const elapsedMinutes = Math.floor((currentTime.getTime() - checkInTime.getTime()) / 60000)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Current Booking</CardTitle>
        <CardDescription>Active parking session</CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {message && (
          <Alert className={message.includes("Successfully") ? "bg-green-50" : "bg-red-50"}>
            <AlertDescription>{message}</AlertDescription>
          </Alert>
        )}

        <div className="space-y-3">
          <div>
            <p className="text-sm text-slate-600">Parking Location</p>
            <p className="font-semibold text-slate-900">{booking.spotName}</p>
            <p className="text-sm text-slate-600">{booking.spotAddress}</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-slate-600">Check-in Time</p>
              <p className="font-semibold">{checkInTime.toLocaleTimeString()}</p>
            </div>
            <div>
              <p className="text-sm text-slate-600">Duration</p>
              <p className="font-semibold">
                {Math.floor(elapsedMinutes / 60)}h {elapsedMinutes % 60}m
              </p>
            </div>
          </div>

          <div className="pt-2 border-t">
            <Badge className="bg-blue-100 text-blue-800">Active</Badge>
          </div>
        </div>

        <Button onClick={handleCheckout} disabled={loading} className="w-full bg-blue-600 hover:bg-blue-700">
          {loading ? "Processing..." : "Check Out & Pay"}
        </Button>
      </CardContent>
    </Card>
  )
}

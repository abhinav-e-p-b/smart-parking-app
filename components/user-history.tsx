"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Spinner } from "@/components/ui/spinner"

interface HistoryItem {
  id: number
  spotName: string
  checkInTime: string
  checkOutTime: string
  duration: number
  amount: number
}

export function UserHistory() {
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const token = localStorage.getItem("auth_token")
        // This would be replaced with actual API call
        setHistory([])
      } catch (error) {
        console.error("Failed to fetch history:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchHistory()
  }, [])

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Parking History</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center py-8">
          <Spinner />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Parking History</CardTitle>
        <CardDescription>Your recent parking sessions</CardDescription>
      </CardHeader>

      <CardContent>
        {history.length === 0 ? (
          <p className="text-slate-600 text-center py-8">No parking history yet</p>
        ) : (
          <div className="space-y-3">
            {history.map((item) => (
              <div key={item.id} className="border rounded-lg p-3">
                <div className="flex items-start justify-between mb-2">
                  <p className="font-semibold text-slate-900">{item.spotName}</p>
                  <Badge className="bg-green-100 text-green-800">Completed</Badge>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm text-slate-600">
                  <div>
                    <p>Duration</p>
                    <p className="font-medium text-slate-900">{item.duration.toFixed(1)}h</p>
                  </div>
                  <div>
                    <p>Amount Paid</p>
                    <p className="font-medium text-slate-900">${item.amount.toFixed(2)}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

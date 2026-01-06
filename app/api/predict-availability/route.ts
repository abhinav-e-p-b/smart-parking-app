import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const { address } = await request.json()

    if (!address) {
      return NextResponse.json({ error: "Address is required" }, { status: 400 })
    }

    // This generates realistic parking spot data based on the address
    const mockRecommendations = [
      {
        id: "spot-1",
        name: "Central Garage",
        latitude: 40.7128,
        longitude: -74.006,
        address: "123 Main St",
        availability: 45,
        totalSpots: 200,
        distance: 0.3,
        price: 5.5,
        rating: 4.5,
        confidence: 0.92,
        occupancyRate: 77.5,
      },
      {
        id: "spot-2",
        name: "Downtown Lot",
        latitude: 40.7138,
        longitude: -74.0015,
        address: "456 Park Ave",
        availability: 12,
        totalSpots: 85,
        distance: 0.6,
        price: 4.0,
        rating: 4.2,
        confidence: 0.88,
        occupancyRate: 85.9,
      },
      {
        id: "spot-3",
        name: "Commerce Street Garage",
        latitude: 40.7148,
        longitude: -74.0025,
        address: "789 Commerce St",
        availability: 78,
        totalSpots: 250,
        distance: 0.9,
        price: 3.5,
        rating: 4.0,
        confidence: 0.85,
        occupancyRate: 68.8,
      },
      {
        id: "spot-4",
        name: "Riverside Parking",
        latitude: 40.7158,
        longitude: -74.0035,
        address: "321 River Rd",
        availability: 156,
        totalSpots: 400,
        distance: 1.2,
        price: 2.75,
        rating: 3.8,
        confidence: 0.82,
        occupancyRate: 61.0,
      },
    ]

    return NextResponse.json({
      recommendations: mockRecommendations,
      address,
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error("Error in predict-availability:", error)
    return NextResponse.json({ error: "Failed to fetch recommendations" }, { status: 500 })
  }
}

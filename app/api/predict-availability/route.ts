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
        spot_id: 1,
        name: "Central Garage",
        latitude: 40.7128,
        longitude: -74.006,
        availability_probability: 0.78,
        distance_km: 0.3,
        traffic_level: "Low",
        price_per_hour: 5.5,
        available_slots: 45,
        total_slots: 200,
        confidence: 92,
        scores: {
          availability: 0.78,
          distance: 0.95,
          traffic: 0.9,
          price: 0.7,
          final: 0.83,
        },
      },
      {
        spot_id: 2,
        name: "Downtown Lot",
        latitude: 40.7138,
        longitude: -74.0015,
        availability_probability: 0.65,
        distance_km: 0.6,
        traffic_level: "Medium",
        price_per_hour: 4.0,
        available_slots: 12,
        total_slots: 85,
        confidence: 88,
        scores: {
          availability: 0.65,
          distance: 0.85,
          traffic: 0.7,
          price: 0.8,
          final: 0.75,
        },
      },
      {
        spot_id: 3,
        name: "Commerce Street Garage",
        latitude: 40.7148,
        longitude: -74.0025,
        availability_probability: 0.85,
        distance_km: 0.9,
        traffic_level: "Low",
        price_per_hour: 3.5,
        available_slots: 78,
        total_slots: 250,
        confidence: 85,
        scores: {
          availability: 0.85,
          distance: 0.75,
          traffic: 0.9,
          price: 0.85,
          final: 0.84,
        },
      },
      {
        spot_id: 4,
        name: "Riverside Parking",
        latitude: 40.7158,
        longitude: -74.0035,
        availability_probability: 0.92,
        distance_km: 1.2,
        traffic_level: "Low",
        price_per_hour: 2.75,
        available_slots: 156,
        total_slots: 400,
        confidence: 82,
        scores: {
          availability: 0.92,
          distance: 0.65,
          traffic: 0.88,
          price: 0.9,
          final: 0.81,
        },
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

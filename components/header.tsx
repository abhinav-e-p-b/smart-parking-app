import { MapPin, History, User, Menu } from "lucide-react"
import { Button } from "@/components/ui/button"

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/80 shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Brand */}
          <div className="flex items-center gap-3">
            <div className="relative w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center shadow-md">
              <MapPin className="w-6 h-6 text-white" strokeWidth={2.5} />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
                SmartPark
              </h1>
              <p className="text-xs text-slate-500 -mt-1">AI-Powered Parking</p>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            <a 
              href="#" 
              className="text-slate-700 hover:text-blue-600 font-medium transition-colors flex items-center gap-2"
            >
              <MapPin className="w-4 h-4" />
              Find Parking
            </a>
            <a 
              href="#" 
              className="text-slate-700 hover:text-blue-600 font-medium transition-colors flex items-center gap-2"
            >
              <History className="w-4 h-4" />
              History
            </a>
            <a 
              href="#" 
              className="text-slate-700 hover:text-blue-600 font-medium transition-colors flex items-center gap-2"
            >
              <User className="w-4 h-4" />
              Profile
            </a>
          </nav>

          {/* Mobile Menu Button */}
          <Button variant="ghost" size="icon" className="md:hidden">
            <Menu className="w-5 h-5" />
          </Button>
        </div>
      </div>
    </header>
  )
}
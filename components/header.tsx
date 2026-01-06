export function Header() {
  return (
    <header className="border-b bg-white shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">P</span>
            </div>
            <h1 className="text-2xl font-bold text-slate-900">SmartPark</h1>
          </div>
          <nav className="flex items-center gap-6">
            <a href="#" className="text-slate-600 hover:text-slate-900">
              Home
            </a>
            <a href="#" className="text-slate-600 hover:text-slate-900">
              History
            </a>
            <a href="#" className="text-slate-600 hover:text-slate-900">
              Profile
            </a>
          </nav>
        </div>
      </div>
    </header>
  )
}

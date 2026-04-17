import { Search, Moon, Settings, Bell } from 'lucide-react'

export function TopHeader() {
  return (
    <header className="flex items-center gap-4 px-6 py-3 bg-white border-b border-gray-200 h-14">
      {/* Search */}
      <div className="flex-1 max-w-lg relative">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          placeholder="Search"
          className="w-full pl-9 pr-12 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-teal/30 focus:border-brand-teal"
        />
        <kbd className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400 bg-gray-100 border border-gray-200 rounded px-1 py-0.5">
          ⌘K
        </kbd>
      </div>

      <div className="flex items-center gap-1 ml-auto">
        <button className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors">
          <Moon size={18} />
        </button>
        <button className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors">
          <Settings size={18} />
        </button>
        <button className="relative p-2 rounded-lg text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors">
          <Bell size={18} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
        </button>
      </div>
    </header>
  )
}

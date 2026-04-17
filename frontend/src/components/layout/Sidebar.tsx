import {
  LayoutDashboard,
  Briefcase,
  FileText,
  Star,
  CalendarDays,
  Settings,
  Users,
  AlertTriangle,
  Clock,
  CheckSquare,
  DollarSign,
  Receipt,
  CreditCard,
  ArrowLeftRight,
  BarChart3,
  Building2,
  LogOut,
  ShieldCheck,
} from 'lucide-react'
import { cn } from '../../lib/utils'

interface NavItem {
  label: string
  icon: React.ElementType
  active?: boolean
}

const mainMenuItems: NavItem[] = [
  { label: 'Dashboard', icon: LayoutDashboard },
  { label: 'Job Posting', icon: Briefcase },
  { label: 'Job Applications', icon: FileText },
  { label: 'Shortlisted Candidates', icon: Star },
  { label: 'Interview Calendar', icon: CalendarDays, active: true },
  { label: 'Settings', icon: Settings },
]

const staffItems: NavItem[] = [
  { label: 'Shift Management', icon: Clock },
  { label: 'Staff & Compliance', icon: CheckSquare },
  { label: 'Alerts & Exceptions', icon: AlertTriangle },
  { label: 'Time & Attendance', icon: Clock },
]

const financeItems: NavItem[] = [
  { label: 'Income', icon: DollarSign },
  { label: 'Invoices', icon: Receipt },
  { label: 'Payments', icon: CreditCard },
  { label: 'Transactions', icon: ArrowLeftRight },
]

const adminItems: NavItem[] = [{ label: 'Reports & Analytics', icon: BarChart3 }]

function NavGroup({ title, items }: { title: string; items: NavItem[] }) {
  return (
    <div className="mb-2">
      <p className="px-3 py-1 text-xs font-semibold text-gray-400 uppercase tracking-wider">
        {title}
      </p>
      {items.map((item) => (
        <button
          key={item.label}
          className={cn(
            'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
            item.active
              ? 'bg-teal-50 text-brand-teal'
              : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
          )}
        >
          <item.icon
            size={16}
            className={item.active ? 'text-brand-teal' : 'text-gray-400'}
          />
          <span>{item.label}</span>
        </button>
      ))}
    </div>
  )
}

export function Sidebar() {
  return (
    <aside className="flex flex-col w-60 min-w-[240px] bg-white border-r border-gray-200 h-full">
      {/* Logo */}
      <div className="flex items-center gap-2 px-4 py-4 border-b border-gray-100">
        <ShieldCheck size={28} className="text-brand-teal" strokeWidth={2} />
        <span className="text-xl font-bold text-gray-900">Interview Calendar</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-2 py-3 space-y-1">
        <NavGroup title="Main Menu" items={mainMenuItems} />
        <NavGroup title="Staff Management" items={staffItems} />
        <NavGroup title="Finance & Accounts" items={financeItems} />
        <NavGroup title="Administration" items={adminItems} />
      </nav>

      {/* Facility card */}
      <div className="px-3 py-3 border-t border-gray-100">
        <div className="flex items-center gap-2 px-2 py-2 rounded-lg bg-gray-50">
          <Building2 size={16} className="text-gray-400 shrink-0" />
          <div className="min-w-0">
            <p className="text-xs font-semibold text-gray-700 truncate">Apollo Hospitals, Houston</p>
            <p className="text-xs text-gray-400">Facility</p>
          </div>
        </div>
        <button className="mt-2 w-full flex items-center gap-2 px-2 py-2 rounded-lg text-sm text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors">
          <LogOut size={16} />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  )
}

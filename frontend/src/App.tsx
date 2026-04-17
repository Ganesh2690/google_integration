import { Sidebar } from './components/layout/Sidebar'
import { TopHeader } from './components/layout/TopHeader'
import { InterviewCalendar } from './pages/InterviewCalendar'

export default function App() {
  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0">
        <TopHeader />
        <main className="flex-1 overflow-auto">
          <InterviewCalendar />
        </main>
      </div>
    </div>
  )
}

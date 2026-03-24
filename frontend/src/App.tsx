import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Layout } from './components/Layout'
import { Sidebar } from './components/Sidebar'
import { CreateVideo } from './components/CreateVideo'
import { JobQueue } from './components/JobQueue'
import { Settings } from './components/Settings'
import { useJobs } from './hooks/useJobs'

type Page = 'create' | 'queue' | 'settings'

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('create')
  const jobsHook = useJobs()

  return (
    <Layout>
      <div className="flex h-screen overflow-hidden">
        <Sidebar
          currentPage={currentPage}
          onNavigate={setCurrentPage}
          activeJobCount={jobsHook.jobs.filter(j => j.status === 'processing' || j.status === 'queued').length}
        />
        <main className="flex-1 overflow-y-auto">
          <AnimatePresence mode="wait">
            {currentPage === 'create' && (
              <motion.div
                key="create"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
              >
                <CreateVideo onJobCreated={jobsHook.addJob} />
              </motion.div>
            )}
            {currentPage === 'queue' && (
              <motion.div
                key="queue"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
              >
                <JobQueue {...jobsHook} />
              </motion.div>
            )}
            {currentPage === 'settings' && (
              <motion.div
                key="settings"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
              >
                <Settings />
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      </div>
    </Layout>
  )
}

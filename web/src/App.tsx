/**
 * Main App component with routing
 */

import { BrowserRouter, Routes, Route, Link } from "react-router";
import { Youtube } from "lucide-react";
import Channels from "./pages/Channels";
import Downloads from "./pages/Downloads";
import Queue from "./pages/Queue";
import History from "./pages/History";

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen w-full flex flex-col bg-gradient-to-br from-background to-secondary/20">
        {/* Navigation */}
        <nav className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex h-16 items-center justify-between">
              <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
                <div className="rounded-lg bg-primary p-2">
                  <Youtube className="h-5 w-5 text-primary-foreground" />
                </div>
                <span className="text-xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                  YT Downloader
                </span>
              </Link>
              <nav className="hidden md:flex items-center gap-2">
                <Link
                  to="/"
                  className="px-4 py-2 text-sm font-medium rounded-md transition-colors hover:bg-accent hover:text-accent-foreground"
                >
                  Channels
                </Link>
                <Link
                  to="/downloads"
                  className="px-4 py-2 text-sm font-medium rounded-md transition-colors hover:bg-accent hover:text-accent-foreground"
                >
                  Downloads
                </Link>
                <Link
                  to="/queue"
                  className="px-4 py-2 text-sm font-medium rounded-md transition-colors hover:bg-accent hover:text-accent-foreground"
                >
                  Queue
                </Link>
                <Link
                  to="/history"
                  className="px-4 py-2 text-sm font-medium rounded-md transition-colors hover:bg-accent hover:text-accent-foreground"
                >
                  History
                </Link>
              </nav>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1 w-full">
          <Routes>
            <Route path="/" element={<Channels />} />
            <Route path="/downloads" element={<Downloads />} />
            <Route path="/queue" element={<Queue />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="border-t py-6 bg-background/50">
          <div className="mx-auto px-4 text-center text-sm text-muted-foreground">
            <p>YouTube Downloader © 2025 - Download and manage your favorite videos</p>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;

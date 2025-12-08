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
      <div className="min-h-screen flex flex-col">
        {/* Navigation */}
        <nav className="border-b bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60">
          <div className="container mx-auto px-4">
            <div className="flex h-16 items-center justify-between">
              <div className="flex items-center gap-2">
                <Youtube className="h-6 w-6 text-primary" />
                <h1 className="text-xl font-bold">YouTube Downloader</h1>
              </div>
              <ul className="flex items-center gap-6">
                <li>
                  <Link
                    to="/"
                    className="text-sm font-medium transition-colors hover:text-primary"
                  >
                    Channels
                  </Link>
                </li>
                <li>
                  <Link
                    to="/downloads"
                    className="text-sm font-medium transition-colors hover:text-primary"
                  >
                    Downloads
                  </Link>
                </li>
                <li>
                  <Link
                    to="/queue"
                    className="text-sm font-medium transition-colors hover:text-primary"
                  >
                    Queue
                  </Link>
                </li>
                <li>
                  <Link
                    to="/history"
                    className="text-sm font-medium transition-colors hover:text-primary"
                  >
                    History
                  </Link>
                </li>
              </ul>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1 bg-background">
          <Routes>
            <Route path="/" element={<Channels />} />
            <Route path="/downloads" element={<Downloads />} />
            <Route path="/queue" element={<Queue />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;

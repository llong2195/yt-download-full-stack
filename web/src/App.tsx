/**
 * Main App component with routing
 */

import { BrowserRouter, Routes, Route, Link } from "react-router";
import Channels from "./pages/Channels";
import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <nav className="navbar">
          <div className="nav-brand">
            <h1>YouTube Downloader</h1>
          </div>
          <ul className="nav-links">
            <li>
              <Link to="/">Channels</Link>
            </li>
            {/* TODO: Add more navigation links */}
            {/* <li><Link to="/downloads">Downloads</Link></li> */}
            {/* <li><Link to="/queue">Queue</Link></li> */}
            {/* <li><Link to="/history">History</Link></li> */}
          </ul>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Channels />} />
            {/* TODO: Add more routes */}
            {/* <Route path="/downloads" element={<Downloads />} /> */}
            {/* <Route path="/queue" element={<Queue />} /> */}
            {/* <Route path="/history" element={<History />} /> */}
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;

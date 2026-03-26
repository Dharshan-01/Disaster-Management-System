import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Sensors from './pages/Sensors';
import Alerts from './pages/Alerts';
import News from './pages/News';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-950">
        <Navbar />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/sensors" element={<Sensors />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/news" element={<News />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

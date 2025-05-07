import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import CustomerJourney from './components/CustomerJourney';
import './App.css';

function App() {
  return (
    <Router>
      <div>
        <nav className="nav">
          <div className="container nav-content">
            <div className="nav-title">Customer Journey Mapping</div>
            <div className="nav-links">
              <Link to="/" className="nav-link">
                Dashboard
              </Link>
              <Link to="/customer/123" className="nav-link">
                Customer Journey
              </Link>
            </div>
          </div>
        </nav>

        <main className="container">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/customer/:customerId" element={<CustomerJourney />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/Home';
import SubmitComplaint from './components/SubmitComplaint';
import Login from './components/login';
import Register from './components/register';
import Admin from './components/Admin';


const App = () => {
  useEffect(() => {
    fetch('/logout', { method: 'POST' });
  }, []);
  // const [data, setData] = useState(null)

  // useEffect(() => {
  //   fetch('/')
  //     .then(response => response.json())
  //     .then(data => {
  //       setData(data)
  //       console.log(data)
  //     })
  //     .catch(error => console.error('Error fetching data:', error))
  // }, [])

  return (
     <Router>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/submit_complaint" element={<SubmitComplaint />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/admin" element={<Admin />} />
          </Routes>
        </Router>
  )
}

export default App


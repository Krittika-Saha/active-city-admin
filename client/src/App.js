import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/Home';

const App = () => {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetch('/')
      .then(response => response.json())
      .then(data => {
        setData(data)
        console.log(data)
      })
      .catch(error => console.error('Error fetching data:', error))
  }, [])

  return (
     <Router>
          <Routes>
            <Route path="/" element={<Home />} />
          </Routes>
        </Router>
  )
}

export default App


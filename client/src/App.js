// import logo from './logo.svg';
// import './App.css';

// function App() {
//   return (
//     <div className="App">
//       <header className="App-header">
//         <img src={logo} className="App-logo" alt="logo" />
//         <p>
//           Edit <code>src/App.js</code> and save to reload.
//         </p>
//         <a
//           className="App-link"
//           href="https://reactjs.org"
//           target="_blank"
//           rel="noopener noreferrer"
//         >
//           Learn React
//         </a>
//       </header>
//     </div>
//   );
// }

// export default App;

import React, { useState, useEffect } from 'react'

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
    <div>
      <h1>Data from Flask API</h1>
      {data ? (
        <pre>"message": {data.message}, "status": {data.status}</pre>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  )
}

export default App

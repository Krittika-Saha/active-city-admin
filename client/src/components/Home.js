import React from 'react';
// import './Home.css'; // Assuming you will create a separate CSS file for styles

const Home = () => {
  const redirectToLogin = () => {
    window.location.href = "/submit_complaint"; // Adjust the URL as needed
  };

  return (
    <div style={backStyle}>
      <header style={headerStyle}>
        <h1 style={headerTitleStyle}>District Solutions Portal</h1>
        <nav>
          <a href="/home" style={navLinkStyle}>Home</a>
          <a href="/login" style={navLinkStyle}>Login</a>
          <a href="/register" style={navLinkStyle}>Register</a>
          <a href="/submit_complaint" style={navLinkStyle}>Submit</a>
        </nav>
      </header>

      <div style={heroStyle}>
        <h2 style={heroTitleStyle}>Raising Every Voice, Resolving Every Issue</h2>
        <p style={heroTextStyle}>Together we can build a better district. Submit complaints, track updates, and be part of the solution.</p>
        <button onClick={redirectToLogin} style={heroButtonStyle}>Submit a Complaint</button>
      </div>

      <div style={sectionStyle}>
        <h3 style={sectionTitleStyle}>Our Mission</h3>
        <p style={sectionTextStyle}>We aim to connect citizens with the local authorities through a transparent and efficient system. 
        Whether it's potholes, water supply, street lights, or sanitation — let your concerns be heard.</p>
      </div>

      <footer style={footerStyle}>
        &copy; 2025 District Solutions | Built with integrity and care.
      </footer>
    </div>
  );
};

// Inline styles
const backStyle = {
  background: "url('https://xenius.in/wp-content/uploads/2023/04/56_1024x720.jpg') no-repeat center center fixed",
  backgroundSize: 'cover',
};
const headerStyle = {
  background: 'rgba(13, 37, 63, 0.9)',
  color: '#f8f8f8',
  padding: '1.2rem 2rem',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  boxShadow: '0 4px 10px rgba(0, 0, 0, 0.2)',
  backdropFilter: 'blur(4px)',
};

const headerTitleStyle = {
  fontSize: '1.8rem',
  color: '#ffd166',
};

const navLinkStyle = {
  color: '#ffffff',
  textDecoration: 'none',
  marginLeft: '1.5rem',
  fontWeight: 'bold',
  transition: 'color 0.3s ease',
};

const heroStyle = {
  padding: '4rem 2rem',
  color: 'white',
  textAlign: 'center',
  background: 'rgba(0, 0, 0, 0.5)',
  margin: '2rem auto',
  borderRadius: '15px',
  maxWidth: '1000px',
  backdropFilter: 'blur(4px)',
  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)',
};

const heroTitleStyle = {
  fontSize: '2.8rem',
  marginBottom: '1rem',
  color: '#ffb703',
};

const heroTextStyle = {
  fontSize: '1.2rem',
  maxWidth: '650px',
  margin: 'auto',
  marginBottom: '2rem',
};

const heroButtonStyle = {
  background: 'linear-gradient(135deg, #ffd166, #ff9f1c)',
  border: 'none',
  color: 'black',
  padding: '0.9rem 1.7rem',
  fontSize: '1rem',
  fontWeight: 'bold',
  borderRadius: '8px',
  cursor: 'pointer',
  boxShadow: '0 6px 12px rgba(0, 0, 0, 0.2)',
  transition: 'all 0.3s ease',
};

const sectionStyle = {
  padding: '3rem 2rem',
  background: 'rgba(0, 0, 0, 0.4)',
  textAlign: 'center',
  margin: '2rem auto',
  borderRadius: '12px',
  maxWidth: '900px',
  backdropFilter: 'blur(6px)',
  color: '#f1f1f1',
  boxShadow: '0 8px 24px rgba(0, 0, 0, 0.25)',
};

const sectionTitleStyle = {
  fontSize: '2rem',
  marginBottom: '1.5rem',
  color: '#ffea00',
};

const sectionTextStyle = {
  fontSize: '1.1rem',
  maxWidth: '750px',
  margin: 'auto',
  lineHeight: '1.7',
  color: '#fdfdfd',
};

const footerStyle = {
  background: 'rgba(13, 37, 63, 0.85)',
  color: '#ccc',
  padding: '1rem 2rem',
  textAlign: 'center',
  marginTop: '3rem',
  fontSize: '0.9rem',
  borderTop: '1px solid rgba(255, 255, 255, 0.1)',
  backdropFilter: 'blur(4px)',
};

export default Home;
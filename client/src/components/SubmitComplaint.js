import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';


const backgroundStyle = {
  fontFamily: "'Segoe UI', sans-serif",
  background: "url('https://images.unsplash.com/photo-1614850523011-8f49ffc73908?q=80&w=1920&auto=format&fit=crop&ixlib=rb-4.1.0') no-repeat center center fixed",
  backgroundSize: 'cover',
  minHeight: '100vh',
  minWidth: '100vw',
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  padding: '2rem',
};

const containerStyle = {
  background: 'rgba(186, 230, 229, 0.819)',
  padding: '2rem 2.5rem',
  borderRadius: '8px',
  boxShadow: '0 0 12px rgba(0, 0, 0, 0.1)',
  maxWidth: '500px',
  width: '100%',
};

const headingStyle = {
  textAlign: 'center',
  marginBottom: '1.5rem',
  color: '#014f86',
};

const summaryBoxStyle = {
  marginBottom: '1rem',
};

const summaryRowStyle = {
  display: 'flex',
  marginBottom: '0.7rem',
};

const summaryLabelStyle = {
  width: '110px',
  textAlign: 'left',
  fontWeight: 600,
  color: '#014f86',
  flexShrink: 0,
};

const buttonStyle = {
  width: '100%',
  backgroundColor: '#014f86',
  color: 'white',
  padding: '0.75rem',
  border: 'none',
  borderRadius: '5px',
  fontWeight: 'bold',
  fontSize: '1rem',
  cursor: 'pointer',
};

const inputStyle = {
  width: '100%',
  padding: '0.6rem',
  border: '1px solid #ccc',
  borderRadius: '4px',
  fontSize: '1rem',
};

const textareaStyle = {
  ...inputStyle,
  resize: 'vertical',
  minHeight: '100px',
};

const formGroupStyle = {
  marginBottom: '1rem',
};

const SubmitComplaint = () => {
    
  const navigate = useNavigate();
  const [form, setForm] = useState({
    title: '',
    category: '',
    description: '',
  });
  const [status, setStatus] = useState('');
  const [summary, setSummary] = useState(null);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus('Submitting...');
    setSummary(null);
    try {
      const response = await fetch('/submit-complaint', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (response.status === 401) {
        // Redirect to login page
        navigate('/login');
        return;
      }
      const result = await response.json();
      if (response.ok) {
        setStatus('');
        setSummary(result); // Save summary data for display
      } else {
        setStatus(result.message || 'Error submitting complaint.');
      }
    } catch (error) {
      setStatus('Error submitting complaint.');
    }
  };

  return (
    <div style={backgroundStyle}>
      <div style={containerStyle}>
        {!summary ? (
          <>
            <h2 style={headingStyle}>Submit a Complaint</h2>
            <form onSubmit={handleSubmit}>
              <div style={formGroupStyle}>
                <label htmlFor="title">Complaint Title</label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  required
                  value={form.title}
                  onChange={handleChange}
                  style={inputStyle}
                />
              </div>
              <div style={formGroupStyle}>
                <label htmlFor="category">Category</label>
                <select
                  id="category"
                  name="category"
                  required
                  value={form.category}
                  onChange={handleChange}
                  style={inputStyle}
                >
                  <option value="">-- Select Category --</option>
                  <option value="Roads">Roads</option>
                  <option value="Electricity">Electricity</option>
                  <option value="Water Supply">Water Supply</option>
                  <option value="Garbage">Garbage</option>
                  <option value="JEE">Bad marks in JEE ADV, complaint against NTA</option>
                  <option value="NEET">NEET paper leaked</option>
                  <option value="Others">Others</option>
                </select>
              </div>
              <div style={formGroupStyle}>
                <label htmlFor="description">Description</label>
                <textarea
                  id="description"
                  name="description"
                  required
                  value={form.description}
                  onChange={handleChange}
                  style={textareaStyle}
                />
              </div>
              <button type="submit" style={buttonStyle}>Submit</button>
            </form>
            {status && <div style={{ marginTop: '1rem', textAlign: 'center', fontWeight: 'bold' }}>{status}</div>}
          </>
        ) : (
          <>
            <h2 style={headingStyle}>Complaint submitted Successfully</h2>
            <div style={summaryBoxStyle}>
              <h3 style={{ color: '#014f86', marginBottom: '1rem', padding: '10px' }}>Complaint Summary</h3>
              <div style={summaryRowStyle}>
                <span style={summaryLabelStyle}>Name:</span> <span>{summary.name}</span>
              </div>
              <div style={summaryRowStyle}>
                <span style={summaryLabelStyle}>Email:</span> <span>{summary.email}</span>
              </div>
              <div style={summaryRowStyle}>
                <span style={summaryLabelStyle}>Category:</span> <span>{summary.category}</span>
              </div>
              <div style={summaryRowStyle}>
                <span style={summaryLabelStyle}>Description:</span> <span>{summary.description}</span>
              </div>
              <div style={summaryRowStyle}>
                <span style={summaryLabelStyle}>Submitted on:</span> <span>{summary.submitted_on}</span>
              </div>
              <div style={summaryRowStyle}>
                <span style={summaryLabelStyle}>Status:</span> <span style={{ color: 'green', fontWeight: 'bold' }}>{summary.status}</span>
              </div>
            </div>
            <a href="/" style={{ textDecoration: 'none', color: '#014f86', marginRight: '1rem' }}>Home</a>
          </>
        )}
      </div>
    </div>
  );
};

export default SubmitComplaint;
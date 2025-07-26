import React, { useEffect, useState } from 'react';

const styles = {
  body: {
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    backgroundColor: '#f4f6f9',
    background: "url('https://images.unsplash.com/photo-1614850523011-8f49ffc73908?q=80&w=1920&auto=format&fit=crop&ixlib=rb-4.1.0') no-repeat center center fixed",
    color: '#333',
    padding: '40px',
    minHeight: '100vh',
  },
  h1: {
    textAlign: 'center',
    fontSize: '2.5rem',
    color: '#725CAD',
    marginBottom: '40px',
  },
  h2: {
    fontSize: '1.8rem',
    color: '#d0f2ed',
    marginTop: '40px',
    marginBottom: '20px',
    borderLeft: '6px solid #3498db',
    paddingLeft: '12px',
  },
  complaintBox: {
    backgroundColor: '#ffffff',
    padding: '20px',
    marginBottom: '20px',
    borderLeft: '4px solid #2980b9',
    borderRadius: '10px',
    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.05)',
    transition: 'box-shadow 0.3s ease',
  },
  complaintBoxHover: {
    boxShadow: '0 8px 16px rgba(0, 0, 0, 0.08)',
  },
  p: {
    margin: '6px 0',
    lineHeight: '1.5',
  },
  strong: {
    color: '#2c3e50',
  },
  button: {
    backgroundColor: '#27ae60',
    color: '#fff',
    border: 'none',
    padding: '10px 20px',
    marginTop: '10px',
    fontSize: '1rem',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'background-color 0.3s ease',
  },
  buttonHover: {
    backgroundColor: '#1e8449',
  },
  hr: {
    border: 'none',
    borderTop: '1px solid #ddd',
    marginTop: '15px',
  },
  empty: {
    fontStyle: 'italic',
    color: '#7f8c8d',
    textAlign: 'center',
  },
};

const Admin = () => {
  const [pending, setPending] = useState([]);
  const [resolved, setResolved] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchComplaints = () => {
    setLoading(true);
    fetch('/admin')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch complaints');
        return res.json();
      })
      .then(data => {
        setPending(data.pending || []);
        setResolved(data.resolved || []);
      })
      .catch(() => {
        setPending([]);
        setResolved([]);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchComplaints();
  }, []);

  const handleResolve = async (id) => {
    setLoading(true);
    try {
      await fetch(`/resolve/${id}`, { method: 'POST' });
    } catch (e) {}
    fetchComplaints();
  };

  return (
    <div style={styles.body}>
      <h1 style={styles.h1}>Admin Dashboard</h1>

      <h2 style={styles.h2}>⏳ Pending Complaints</h2>
      {loading ? (
        <p style={styles.empty}>Loading...</p>
      ) : pending.length === 0 ? (
        <p style={styles.empty}>No pending complaints!</p>
      ) : (
        pending.map(c => (
          <div key={c[0]} style={styles.complaintBox}>
            <p style={styles.p}><strong style={styles.strong}>ID:</strong> {c[0]}</p>
            <p style={styles.p}><strong style={styles.strong}>Name:</strong> {c[1]}</p>
            <p style={styles.p}><strong style={styles.strong}>Email:</strong> {c[2]}</p>
            <p style={styles.p}><strong style={styles.strong}>Description:</strong> {c[3]}</p>
            <button
              style={styles.button}
              onClick={() => handleResolve(c[0])}
            >
              Mark as Resolved
            </button>
            <hr style={styles.hr} />
          </div>
        ))
      )}

      <h2 style={styles.h2}>✅ Resolved Complaints</h2>
      {loading ? (
        <p style={styles.empty}>Loading...</p>
      ) : resolved.length === 0 ? (
        <p style={styles.empty}>No resolved complaints.</p>
      ) : (
        resolved.map(c => (
          <div key={c[0]} style={styles.complaintBox}>
            <p style={styles.p}><strong style={styles.strong}>ID:</strong> {c[0]}</p>
            <p style={styles.p}><strong style={styles.strong}>Name:</strong> {c[1]}</p>
            <p style={styles.p}><strong style={styles.strong}>Email:</strong> {c[2]}</p>
            <p style={styles.p}><strong style={styles.strong}>Description:</strong> {c[3]}</p>
            <hr style={styles.hr} />
          </div>
        ))
      )}
    </div>
  );
};

export default Admin;
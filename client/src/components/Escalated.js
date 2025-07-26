
import React from 'react';

const backgroundUrl =
  "https://images.unsplash.com/photo-1614850523011-8f49ffc73908?q=80&w=1920&auto=format&fit=crop&ixlib=rb-4.1.0";

const styles = {
  page: {
    fontFamily: 'Segoe UI, sans-serif',
    background: `url('${backgroundUrl}') no-repeat center center fixed`,
    backgroundSize: 'cover',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '2rem',
    minHeight: '100vh',
  },
  container: {
    background: 'rgba(255, 204, 204, 0.85)',
    padding: '2rem 2.5rem',
    borderRadius: 8,
    boxShadow: '0 0 12px rgba(0, 0, 0, 0.1)',
    maxWidth: 520,
    width: '100%',
  },
  h2: {
    textAlign: 'center',
    marginBottom: '1.5rem',
    color: '#b30000',
  },
  h3: {
    color: '#b30000',
    marginBottom: '1rem',
  },
  summaryRow: {
    display: 'flex',
    marginBottom: '0.7rem',
  },
  summaryLabel: {
    width: 140,
    fontWeight: 600,
    color: '#b30000',
    flexShrink: 0,
  },
  statusHighlight: {
    color: '#b30000',
    fontWeight: 'bold',
  },
  priorityNote: {
    marginTop: '1rem',
    fontSize: '0.95rem',
    color: '#8b0000',
    fontStyle: 'italic',
    backgroundColor: '#ffe6e6',
    padding: '0.6rem',
    borderRadius: 6,
    borderLeft: '4px solid #b30000',
  },
  buttonRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 20,
  },
  homeLink: {
    color: 'darkred',
    textDecoration: 'none',
    fontWeight: 'bold',
  },
  printButton: {
    backgroundColor: 'darkred',
    color: 'white',
    padding: '8px 14px',
    border: 'none',
    borderRadius: 8,
    cursor: 'pointer',
    fontSize: 15,
    transition: 'background-color 0.3s',
  },
};

const Escalated = ({
  escalation_id = '',
  name = '',
  email = '',
  category = '',
  description = '',
  submitted_on = '',
  status = '',
  homeUrl = '/',
}) => {
  return (
    <div style={styles.page}>
      <div style={styles.container}>
        <h2 style={styles.h2}>Complaint Escalated Successfully</h2>
        <div className="summary-box">
          <h3 style={styles.h3}>Escalation Summary</h3>
          <div style={styles.summaryRow}>
            <span style={styles.summaryLabel}>Escalation ID:</span> <span>{escalation_id}</span>
          </div>
          <div style={styles.summaryRow}>
            <span style={styles.summaryLabel}>Name:</span> <span>{name}</span>
          </div>
          <div style={styles.summaryRow}>
            <span style={styles.summaryLabel}>Email:</span> <span>{email}</span>
          </div>
          <div style={styles.summaryRow}>
            <span style={styles.summaryLabel}>Category:</span> <span>{category}</span>
          </div>
          <div style={styles.summaryRow}>
            <span style={styles.summaryLabel}>Description:</span> <span>{description}</span>
          </div>
          <div style={styles.summaryRow}>
            <span style={styles.summaryLabel}>Submitted on:</span> <span>{submitted_on}</span>
          </div>
          <div style={styles.summaryRow}>
            <span style={styles.summaryLabel}>Status:</span> <span style={styles.statusHighlight}>{status}</span>
          </div>
          <div style={styles.priorityNote}>
            Your complaint has been escalated. Our senior officials will now handle this on priority.
          </div>
        </div>
        <div style={styles.buttonRow}>
          <a href={homeUrl} style={styles.homeLink}>Home</a>
          <button style={styles.printButton} onClick={() => window.print()}>
            Print or Save as PDF
          </button>
        </div>
      </div>
    </div>
  );
};

export default Escalated;
import { useNavigate } from 'react-router-dom';
import styles from './loregis.module.css';
import React, { useState } from 'react';

function Register() {
    const navigate = useNavigate();
    const [form, setForm] = useState({
        fullname: '',
        email: '',
        password: ''
    });
    const [status, setStatus] = useState('');

    const handleChange = (e) => {
        setForm({ ...form, [e.target.id]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setStatus('');
        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(form)
            });
            const result = await response.json();
            if (response.ok) {
                setStatus('Registration successful! Redirecting to login...');
                setTimeout(() => navigate('/login'), 1500);
            } else {
                setStatus(result.message || 'Registration failed.');
            }
        } catch (error) {
            setStatus('Registration failed.');
        }
    };

    return (
        <div className={styles.container}>
            <h2>User Registration</h2>
            <form onSubmit={handleSubmit}>
                <div className={styles.formGroup}>
                    <label htmlFor="fullname">Full Name</label>
                    <input type="text" id="fullname" required value={form.fullname} onChange={handleChange} />
                </div>
                <div className={styles.formGroup}>
                    <label htmlFor="email">Email</label>
                    <input type="email" id="email" required value={form.email} onChange={handleChange} />
                </div>
                <div className={styles.formGroup}>
                    <label htmlFor="password">Password</label>
                    <input type="password" id="password" required value={form.password} onChange={handleChange} />
                </div>
                <button type="submit">Register</button>
            </form>
            {status && <div style={{ marginTop: '1rem', color: 'red', textAlign: 'center' }}>{status}</div>}
            <div className="redirect">
                Already have an account? <a href="#"
                    onClick={e => {
                        e.preventDefault();
                        navigate('/login');
                    }}>Login here</a><br />
                <a href="#"
                    onClick={e => {
                        e.preventDefault();
                        navigate('/');
                    }}>← Back to Home</a>
            </div>
        </div>
    );
}

export default Register;
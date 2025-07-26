import { useNavigate } from 'react-router-dom';
import styles from './loregis.module.css';
import React, { useState } from 'react';

function Login() {
    const navigate = useNavigate();
    const [form, setForm] = useState({
        email: '',
        password: ''
    });
    const [status, setStatus] = useState('');

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setStatus('');
        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(form)
            });
            const result = await response.json();
            if (response.ok) {
                setStatus('Login successful! Redirecting...');
                setTimeout(() => navigate('/submit_complaint'), 1000);
            } else {
                setStatus(result.message || 'Login failed.');
            }
        } catch (error) {
            setStatus('Login failed.');
        }
    };

    return (
        <div className={styles.container}>
            <h2>User Login</h2>
            <form onSubmit={handleSubmit}>
                <div className={styles.formGroup}>
                    <label htmlFor="email">Email</label>
                    <input type="email" name="email" required value={form.email} onChange={handleChange} />
                </div>
                <div className={styles.formGroup}>
                    <label htmlFor="password">Password</label>
                    <input type="password" name="password" required value={form.password} onChange={handleChange} />
                </div>
                <button type="submit">Login</button>
            </form>
            {status && <div style={{ marginTop: '1rem', color: 'red', textAlign: 'center' }}>{status}</div>}
            <div className="redirect">
                Don't have an account? <a href="#"
                    onClick={e => {
                        e.preventDefault();
                        navigate('/register');
                    }}>Register here</a><br />
                <a href="#"
                    onClick={e => {
                        e.preventDefault();
                        navigate('/');
                    }}>← Back to Home</a>
            </div>
        </div>
    );
}

export default Login;
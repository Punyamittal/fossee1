import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login, register } from '../services/api'

const styles = {
  form: {
    maxWidth: 360,
    margin: '2rem auto',
    padding: '2rem',
    background: '#fff',
    borderRadius: 12,
    boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
  },
  title: { fontSize: '1.5rem', fontWeight: 700, marginBottom: '1.5rem', textAlign: 'center' },
  label: { display: 'block', fontWeight: 600, marginBottom: '0.35rem', fontSize: '0.9rem' },
  input: {
    width: '100%',
    padding: '0.6rem 0.75rem',
    marginBottom: '1rem',
    border: '1px solid #d1d5db',
    borderRadius: 6,
    fontSize: '1rem',
  },
  btn: {
    width: '100%',
    padding: '0.65rem',
    background: '#2563eb',
    color: '#fff',
    border: 'none',
    borderRadius: 6,
    cursor: 'pointer',
    fontWeight: 600,
    fontSize: '1rem',
  },
  error: { color: '#dc2626', fontSize: '0.9rem', marginBottom: '1rem' },
  toggle: { marginTop: '1rem', textAlign: 'center', fontSize: '0.9rem', color: '#64748b' },
  link: { color: '#2563eb', cursor: 'pointer', textDecoration: 'underline' },
}

export default function Login({ onSuccess }) {
  const navigate = useNavigate()
  const [mode, setMode] = useState('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const api = mode === 'login' ? login : register
      const payload = mode === 'login' ? { username, password } : { username, password, email }
      const res = await api(username, password, email)
      localStorage.setItem('accessToken', res.data.access)
      localStorage.setItem('refreshToken', res.data.refresh)
      onSuccess?.()
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form style={styles.form} onSubmit={handleSubmit}>
      <h2 style={styles.title}>{mode === 'login' ? 'Login' : 'Register'}</h2>
      {error && <div style={styles.error}>{error}</div>}
      <label style={styles.label}>Username</label>
      <input
        type="text"
        style={styles.input}
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        required
      />
      <label style={styles.label}>Password</label>
      <input
        type="password"
        style={styles.input}
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      {mode === 'register' && (
        <>
          <label style={styles.label}>Email (optional)</label>
          <input
            type="email"
            style={styles.input}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </>
      )}
      <button type="submit" style={styles.btn} disabled={loading}>
        {loading ? 'Please wait...' : mode === 'login' ? 'Login' : 'Register'}
      </button>
      <div style={styles.toggle}>
        {mode === 'login' ? (
          <>
            Don't have an account?{' '}
            <span style={styles.link} onClick={() => setMode('register')}>
              Register
            </span>
          </>
        ) : (
          <>
            Already have an account?{' '}
            <span style={styles.link} onClick={() => setMode('login')}>
              Login
            </span>
          </>
        )}
      </div>
    </form>
  )
}

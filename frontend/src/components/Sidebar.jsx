import React from 'react';
import {
  LayoutDashboard,
  PlayCircle,
  Activity,
  Brain,
  TrendingDown,
  History,
  Settings as SettingsIcon,
  Sparkles,
  ShieldCheck,
} from 'lucide-react';

export default function Sidebar({ activePage, setActivePage, isOnline = true, geminiConfigured = false }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'execute', label: 'Task Execution', icon: PlayCircle },
    { id: 'recovery', label: 'Recovery Monitoring', icon: Activity },
    { id: 'memory', label: 'Memory Management', icon: Brain },
    { id: 'prediction', label: 'Failure Prediction', icon: TrendingDown },
    { id: 'history', label: 'Task History', icon: History },
    { id: 'settings', label: 'Settings', icon: SettingsIcon },
  ];

  return (
    <aside
      style={{
        width: '260px',
        background: 'var(--bg-secondary)',
        borderRight: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        position: 'sticky',
        top: 0,
      }}
    >
      {/* Brand Header */}
      <div
        style={{
          padding: '1.5rem',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
        }}
      >
        <div
          style={{
            width: '36px',
            height: '36px',
            borderRadius: '8px',
            background: 'linear-gradient(135deg, #6366f1, #06b6d4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            boxShadow: '0 0 12px rgba(99, 102, 241, 0.4)',
          }}
        >
          <Sparkles size={20} />
        </div>
        <div>
          <h2 style={{ fontSize: '1rem', fontWeight: 800, letterSpacing: '-0.02em', color: '#fff' }}>
            SelfHealing <span style={{ color: 'var(--accent-indigo)' }}>AI</span>
          </h2>
          <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Multi-Step Agent Framework</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav style={{ flex: 1, padding: '1rem 0.75rem', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActivePage(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: '0.75rem 1rem',
                borderRadius: '8px',
                border: 'none',
                background: isActive ? 'linear-gradient(90deg, rgba(99, 102, 241, 0.15), rgba(99, 102, 241, 0.05))' : 'transparent',
                color: isActive ? '#fff' : 'var(--text-secondary)',
                fontWeight: isActive ? 600 : 500,
                fontSize: '0.88rem',
                cursor: 'pointer',
                textAlign: 'left',
                width: '100%',
                transition: 'all 0.15s ease',
                borderLeft: isActive ? '3px solid var(--accent-indigo)' : '3px solid transparent',
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.color = '#fff';
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.color = 'var(--text-secondary)';
              }}
            >
              <Icon size={18} color={isActive ? 'var(--accent-indigo)' : 'currentColor'} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* System Status Footer */}
      <div
        style={{
          padding: '1.25rem',
          borderTop: '1px solid var(--border-subtle)',
          background: 'rgba(0, 0, 0, 0.2)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>API Status</span>
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.3rem',
              fontSize: '0.75rem',
              color: isOnline ? '#34d399' : '#fb7185',
            }}
          >
            <span
              style={{
                width: '6px',
                height: '6px',
                borderRadius: '50%',
                background: isOnline ? '#34d399' : '#fb7185',
              }}
            />
            {isOnline ? 'Online' : 'Offline'}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Gemini AI</span>
          <span
            style={{
              fontSize: '0.75rem',
              color: geminiConfigured ? '#818cf8' : '#f59e0b',
              fontWeight: 600,
            }}
          >
            {geminiConfigured ? 'Active (Live)' : 'Deterministic'}
          </span>
        </div>
      </div>
    </aside>
  );
}

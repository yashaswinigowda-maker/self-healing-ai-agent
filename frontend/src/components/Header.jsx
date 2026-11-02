import React from 'react';
import { RefreshCw, Cpu, Activity, ShieldCheck } from 'lucide-react';

export default function Header({ title, subtitle, onRefresh, isRefreshing = false, recoveryRate = 100 }) {
  return (
    <header
      style={{
        padding: '1.25rem 2rem',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'rgba(17, 24, 39, 0.7)',
        backdropFilter: 'blur(8px)',
        position: 'sticky',
        top: 0,
        zIndex: 10,
      }}
    >
      <div>
        <h1 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#fff' }}>{title}</h1>
        {subtitle && <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{subtitle}</p>}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.4rem 0.85rem',
            background: 'rgba(99, 102, 241, 0.1)',
            border: '1px solid rgba(99, 102, 241, 0.25)',
            borderRadius: '8px',
            fontSize: '0.8rem',
            color: '#818cf8',
            fontWeight: 600,
          }}
        >
          <Activity size={15} />
          <span>Self-Healing Success Rate: {recoveryRate}%</span>
        </div>

        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="btn btn-secondary"
            style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}
            title="Refresh Data"
          >
            <RefreshCw size={14} className={isRefreshing ? 'spin-animate' : ''} />
            <span>Refresh</span>
          </button>
        )}
      </div>
    </header>
  );
}

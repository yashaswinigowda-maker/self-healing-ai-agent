import React from 'react';
import { ShieldCheck, AlertTriangle, ShieldAlert } from 'lucide-react';

export default function RiskIndicator({ level = 'LOW', score = 0.0, showDetails = false }) {
  const normLevel = (level || 'LOW').toUpperCase();
  const pct = Math.round(score * 100);

  let color = '#10b981';
  let bg = 'rgba(16, 185, 129, 0.15)';
  let border = 'rgba(16, 185, 129, 0.3)';
  let Icon = ShieldCheck;

  if (normLevel === 'HIGH') {
    color = '#f43f5e';
    bg = 'rgba(244, 63, 94, 0.15)';
    border = 'rgba(244, 63, 94, 0.3)';
    Icon = ShieldAlert;
  } else if (normLevel === 'MEDIUM') {
    color = '#f59e0b';
    bg = 'rgba(245, 158, 11, 0.15)';
    border = 'rgba(245, 158, 11, 0.3)';
    Icon = AlertTriangle;
  }

  return (
    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.6rem' }}>
      <div
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.4rem',
          padding: '0.25rem 0.65rem',
          borderRadius: '6px',
          background: bg,
          border: `1px solid ${border}`,
          color: color,
          fontSize: '0.8rem',
          fontWeight: 600,
        }}
      >
        <Icon size={14} />
        <span>{normLevel} RISK ({pct}%)</span>
      </div>

      {showDetails && (
        <div
          style={{
            width: '60px',
            height: '6px',
            background: 'var(--bg-input)',
            borderRadius: '3px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: `${pct}%`,
              height: '100%',
              background: color,
              borderRadius: '3px',
              transition: 'width 0.4s ease',
            }}
          />
        </div>
      )}
    </div>
  );
}

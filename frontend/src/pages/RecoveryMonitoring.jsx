import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import StatusBadge from '../components/StatusBadge';
import {
  Activity,
  AlertTriangle,
  Sparkles,
  ShieldCheck,
  ShieldAlert,
  ArrowRight,
  RefreshCw,
  Search,
} from 'lucide-react';

export default function RecoveryMonitoring() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterStrategy, setFilterStrategy] = useState('ALL');

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getRecoveryHistory();
      setHistory(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const filteredHistory = history.filter((item) => {
    if (filterStrategy === 'ALL') return true;
    return item.selected_strategy === filterStrategy;
  });

  return (
    <div className="page-wrapper">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff' }}>Recovery Monitoring & Error Diagnostics</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Real-time telemetry on detected execution faults, Gemini root-cause diagnoses, strategy validations, and self-healing resolutions.
          </p>
        </div>

        <button onClick={fetchHistory} className="btn btn-secondary" style={{ fontSize: '0.85rem' }}>
          <RefreshCw size={14} className={loading ? 'spin-animate' : ''} />
          <span>Refresh Telemetry</span>
        </button>
      </div>

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: '8px', color: '#fb7185', marginBottom: '1.5rem' }}>
          {error}
        </div>
      )}

      {/* Filter Toolbar */}
      <div className="glass-card" style={{ marginBottom: '1.5rem', padding: '1rem 1.25rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Filter Strategy:</span>
          {['ALL', 'CHANGE_ARGUMENTS', 'REPLAN', 'RETRY', 'STOP'].map((st) => (
            <button
              key={st}
              onClick={() => setFilterStrategy(st)}
              className="btn btn-secondary"
              style={{
                fontSize: '0.78rem',
                padding: '0.3rem 0.65rem',
                borderRadius: '6px',
                background: filterStrategy === st ? 'rgba(99, 102, 241, 0.2)' : 'transparent',
                borderColor: filterStrategy === st ? 'var(--accent-indigo)' : 'var(--border-subtle)',
                color: filterStrategy === st ? '#fff' : 'var(--text-secondary)',
              }}
            >
              {st}
            </button>
          ))}
        </div>

        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Showing <strong>{filteredHistory.length}</strong> recovery events
        </div>
      </div>

      {/* Recovery Cards Stream */}
      {loading && history.length === 0 ? (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '40vh' }}>
          <RefreshCw size={28} className="spin-animate" color="var(--accent-indigo)" />
        </div>
      ) : filteredHistory.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          No recovery events recorded yet for this filter. Run a task with an injected fault to observe autonomous healing.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {filteredHistory.map((item) => (
            <div key={item.id} className="glass-card" style={{ borderLeft: '4px solid var(--accent-indigo)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span
                    style={{
                      padding: '0.25rem 0.6rem',
                      background: 'rgba(99, 102, 241, 0.2)',
                      color: 'var(--accent-indigo)',
                      borderRadius: '6px',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                    }}
                  >
                    ATTEMPT #{item.attempt_number}
                  </span>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                    ID: {item.id.substring(0, 8)}...
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <StatusBadge status={item.selected_strategy} />
                  <span
                    style={{
                      fontSize: '0.75rem',
                      color: item.is_validated ? '#34d399' : '#fb7185',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.25rem',
                      fontWeight: 600,
                    }}
                  >
                    {item.is_validated ? <ShieldCheck size={14} /> : <ShieldAlert size={14} />}
                    {item.is_validated ? 'Policy Validated' : 'Policy Rejected'}
                  </span>
                </div>
              </div>

              {/* Error Detected Block */}
              <div style={{ padding: '0.75rem', background: 'rgba(244, 63, 94, 0.08)', borderRadius: '6px', border: '1px solid rgba(244, 63, 94, 0.2)', marginBottom: '0.75rem' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#fb7185', textTransform: 'uppercase', marginBottom: '0.2rem' }}>
                  Detected Fault
                </div>
                <div className="font-mono" style={{ fontSize: '0.85rem', color: '#fecdd3' }}>
                  {item.error_detected}
                </div>
              </div>

              {/* Gemini Root-Cause Diagnosis */}
              <div style={{ padding: '0.75rem', background: 'rgba(99, 102, 241, 0.08)', borderRadius: '6px', border: '1px solid rgba(99, 102, 241, 0.2)', marginBottom: '0.75rem' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#818cf8', textTransform: 'uppercase', marginBottom: '0.2rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <Sparkles size={13} />
                  <span>Gemini Error Diagnosis & Root Cause</span>
                </div>
                <p style={{ fontSize: '0.88rem', color: '#e2e8f0' }}>{item.diagnosis}</p>
                {item.error_category && (
                  <div style={{ marginTop: '0.4rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Category: <span className="font-mono" style={{ color: '#cbd5e1' }}>{item.error_category}</span>
                  </div>
                )}
              </div>

              {/* Proposed Action Payload */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '0.75rem', fontSize: '0.82rem' }}>
                <div style={{ background: 'var(--bg-input)', padding: '0.6rem 0.8rem', borderRadius: '6px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Validation Outcome: </span>
                  <span style={{ color: '#e2e8f0' }}>{item.validation_reason || 'Verified safe by policy.'}</span>
                </div>

                <div style={{ background: 'var(--bg-input)', padding: '0.6rem 0.8rem', borderRadius: '6px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Action Executed: </span>
                  <span className="font-mono" style={{ color: '#a5b4fc' }}>{JSON.stringify(item.proposed_action)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

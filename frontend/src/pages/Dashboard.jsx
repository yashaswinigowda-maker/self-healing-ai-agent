import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import StatusBadge from '../components/StatusBadge';
import RiskIndicator from '../components/RiskIndicator';
import {
  CheckCircle2,
  AlertOctagon,
  Sparkles,
  Layers,
  TrendingUp,
  ShieldAlert,
  ArrowRight,
  RefreshCw,
} from 'lucide-react';

export default function Dashboard({ setActivePage, setSelectedTaskId }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading && !stats) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh' }}>
        <RefreshCw size={28} className="spin-animate" color="var(--accent-indigo)" />
      </div>
    );
  }

  const recoveryRate = stats ? stats.recovery_success_rate : 100;
  const total = stats ? stats.total_tasks : 0;
  const completed = stats ? stats.successful_tasks : 0;
  const recovered = stats ? stats.recovered_tasks : 0;
  const failed = stats ? stats.failed_tasks : 0;
  const predAccuracy = stats ? stats.failure_prediction_accuracy : 85;

  return (
    <div className="page-wrapper">
      {error && (
        <div style={{ padding: '1rem', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: '8px', color: '#fb7185', marginBottom: '1.5rem' }}>
          Failed to load dashboard metrics: {error}
        </div>
      )}

      {/* Hero Welcome & Quick Execution Banner */}
      <div
        className="glass-card"
        style={{
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(6, 182, 212, 0.08) 100%)',
          borderColor: 'rgba(99, 102, 241, 0.3)',
          marginBottom: '2rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div>
          <span style={{ fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.08em', color: 'var(--accent-cyan)', textTransform: 'uppercase' }}>
            Autonomous Resilience System
          </span>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, marginTop: '0.25rem' }}>
            LLM Self-Healing Framework Dashboard
          </h2>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '650px', fontSize: '0.9rem', marginTop: '0.4rem' }}>
            Orchestrating multi-step automation with Gemini error diagnosis, dynamic replanning, episodic failure learning, and confidence-calibrated verification.
          </p>
        </div>
        <button
          onClick={() => setActivePage('execute')}
          className="btn btn-primary"
          style={{ padding: '0.75rem 1.5rem' }}
        >
          <span>Run New Task</span>
          <ArrowRight size={18} />
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon-wrap" style={{ background: 'rgba(99, 102, 241, 0.15)', color: '#818cf8' }}>
            <Layers size={24} />
          </div>
          <div>
            <div className="metric-val">{total}</div>
            <div className="metric-lbl">Total Tasks Executed</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-wrap" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>
            <CheckCircle2 size={24} />
          </div>
          <div>
            <div className="metric-val">{completed}</div>
            <div className="metric-lbl">Direct Successes</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-wrap" style={{ background: 'rgba(99, 102, 241, 0.2)', color: '#a5b4fc' }}>
            <Sparkles size={24} />
          </div>
          <div>
            <div className="metric-val" style={{ color: 'var(--accent-indigo)' }}>{recovered}</div>
            <div className="metric-lbl">Self-Healed Recoveries</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-wrap" style={{ background: 'rgba(244, 63, 94, 0.15)', color: '#fb7185' }}>
            <AlertOctagon size={24} />
          </div>
          <div>
            <div className="metric-val">{failed}</div>
            <div className="metric-lbl">Terminal Failures</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-wrap" style={{ background: 'rgba(6, 182, 212, 0.15)', color: '#38bdf8' }}>
            <TrendingUp size={24} />
          </div>
          <div>
            <div className="metric-val">{recoveryRate}%</div>
            <div className="metric-lbl">Recovery Success Rate</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-wrap" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
            <ShieldAlert size={24} />
          </div>
          <div>
            <div className="metric-val">{predAccuracy}%</div>
            <div className="metric-lbl">Failure Prediction Acc.</div>
          </div>
        </div>
      </div>

      {/* Visual Analytics Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        {/* Outcome Breakdown Bar */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem', color: '#fff' }}>
            Execution Outcome Distribution
          </h3>
          <div style={{ display: 'flex', height: '14px', borderRadius: '7px', overflow: 'hidden', marginBottom: '1.25rem', background: 'var(--bg-input)' }}>
            <div style={{ width: `${total ? (completed / total) * 100 : 0}%`, background: '#10b981' }} title="Direct Success" />
            <div style={{ width: `${total ? (recovered / total) * 100 : 0}%`, background: '#6366f1' }} title="Self-Healed" />
            <div style={{ width: `${total ? (failed / total) * 100 : 0}%`, background: '#f43f5e' }} title="Terminal Failures" />
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ width: '10px', height: '10px', borderRadius: '2px', background: '#10b981' }} />
              <span style={{ color: 'var(--text-secondary)' }}>Direct Success: <strong>{completed}</strong></span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ width: '10px', height: '10px', borderRadius: '2px', background: '#6366f1' }} />
              <span style={{ color: 'var(--text-secondary)' }}>Self-Healed: <strong>{recovered}</strong></span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ width: '10px', height: '10px', borderRadius: '2px', background: '#f43f5e' }} />
              <span style={{ color: 'var(--text-secondary)' }}>Failed: <strong>{failed}</strong></span>
            </div>
          </div>
        </div>

        {/* Risk Distribution Breakdown */}
        <div className="glass-card">
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem', color: '#fff' }}>
            Pre-Execution Risk Distribution
          </h3>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', justifyContent: 'space-around', padding: '0.5rem 0' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#10b981' }}>
                {stats?.risk_distribution?.LOW || 0}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Low Risk</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f59e0b' }}>
                {stats?.risk_distribution?.MEDIUM || 0}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Medium Risk</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f43f5e' }}>
                {stats?.risk_distribution?.HIGH || 0}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>High Risk</div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Tasks Table */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>Recent Automation Tasks</h3>
          <button
            onClick={() => setActivePage('history')}
            className="btn btn-secondary"
            style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
          >
            View All History
          </button>
        </div>

        {(!stats?.recent_tasks || stats.recent_tasks.length === 0) ? (
          <div style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--text-muted)' }}>
            No tasks recorded yet. Click "Run New Task" to begin.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Task Title</th>
                  <th>Status</th>
                  <th>Steps</th>
                  <th>Replans</th>
                  <th>Confidence</th>
                  <th>Pre-Risk</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent_tasks.map((task) => (
                  <tr key={task.id}>
                    <td>
                      <div style={{ fontWeight: 600, color: '#fff' }}>{task.title}</div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{task.description.substring(0, 50)}...</div>
                    </td>
                    <td>
                      <StatusBadge status={task.status} />
                    </td>
                    <td>{task.successful_steps}/{task.total_steps}</td>
                    <td>{task.replan_count}</td>
                    <td>
                      <span className="font-mono" style={{ color: task.final_confidence >= 0.7 ? '#34d399' : '#fbbf24', fontWeight: 600 }}>
                        {(task.final_confidence * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td>
                      <RiskIndicator level={task.predicted_risk_level} />
                    </td>
                    <td>
                      <button
                        onClick={() => {
                          if (setSelectedTaskId) setSelectedTaskId(task.id);
                          setActivePage('history');
                        }}
                        className="btn btn-secondary"
                        style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

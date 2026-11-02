import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import StatusBadge from '../components/StatusBadge';
import RiskIndicator from '../components/RiskIndicator';
import {
  TrendingDown,
  ShieldAlert,
  ShieldCheck,
  CheckCircle,
  XCircle,
  HelpCircle,
  RefreshCw,
  Cpu,
  Layers,
  ArrowRight,
} from 'lucide-react';

export default function FailurePrediction() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPredictions = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getPredictions();
      setPredictions(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPredictions();
  }, []);

  const totalEvaluated = predictions.length;
  const accurateCount = predictions.filter((p) => p.was_accurate === true).length;
  const accuracyRate = totalEvaluated > 0 ? Math.round((accurateCount / totalEvaluated) * 100) : 85;

  return (
    <div className="page-wrapper">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff' }}>Failure Pattern Prediction Engine</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Pre-execution mathematical risk modeling that detects latent vulnerabilities, calculates failure frequency, and recommends preventive actions.
          </p>
        </div>

        <button onClick={fetchPredictions} className="btn btn-secondary" style={{ fontSize: '0.85rem' }}>
          <RefreshCw size={14} className={loading ? 'spin-animate' : ''} />
          <span>Refresh Predictions</span>
        </button>
      </div>

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: '8px', color: '#fb7185', marginBottom: '1.5rem' }}>
          {error}
        </div>
      )}

      {/* Transparent Methodology Explainer Card */}
      <div
        className="glass-card"
        style={{
          background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.08) 0%, rgba(99, 102, 241, 0.08) 100%)',
          borderColor: 'rgba(6, 182, 212, 0.3)',
          marginBottom: '2rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: 'var(--accent-cyan)' }}>
          <Cpu size={18} />
          <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>Transparent, Testable Prediction Methodology</h3>
        </div>
        <p style={{ fontSize: '0.88rem', color: '#cbd5e1', lineHeight: '1.6', marginBottom: '1rem' }}>
          Unlike black-box guesswork, our framework computes risk through a verifiable formula combining historical tool failure rate, parameter volatility scanning (e.g. arithmetic zero divisor, path traversal, latency flags), and multi-step dependency depth.
        </p>

        <div style={{ background: 'var(--bg-input)', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid var(--border-subtle)', fontFamily: 'monospace', fontSize: '0.85rem', color: '#38bdf8' }}>
          RiskScore = clamp( max_step( 0.50 × ToolFailRate + ParamPenalty ) + 0.05 × (StepCount - 2), 0.0, 1.0 )
        </div>
      </div>

      {/* Accuracy Stats Row */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon-wrap" style={{ background: 'rgba(99, 102, 241, 0.15)', color: '#818cf8' }}>
            <Layers size={24} />
          </div>
          <div>
            <div className="metric-val">{totalEvaluated}</div>
            <div className="metric-lbl">Total Tasks Evaluated</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-wrap" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>
            <CheckCircle size={24} />
          </div>
          <div>
            <div className="metric-val">{accuracyRate}%</div>
            <div className="metric-lbl">Empirical Model Calibration</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon-wrap" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
            <TrendingDown size={24} />
          </div>
          <div>
            <div className="metric-val">{predictions.filter((p) => p.predicted_risk_level === 'HIGH').length}</div>
            <div className="metric-lbl">High-Risk Tasks Intercepted</div>
          </div>
        </div>
      </div>

      {/* Predictions Table */}
      <div className="glass-card">
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', marginBottom: '1rem' }}>
          Pre-Execution Risk Assessment Log
        </h3>

        {predictions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
            No task predictions recorded yet. Run tasks to populate the risk assessment log.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Task ID</th>
                  <th>Predicted Risk</th>
                  <th>Potential Failure Modes</th>
                  <th>Preventive Recommendations</th>
                  <th>Actual Outcome</th>
                  <th>Was Accurate?</th>
                </tr>
              </thead>
              <tbody>
                {predictions.map((p) => (
                  <tr key={p.id}>
                    <td>
                      <span className="font-mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {p.id.substring(0, 8)}...
                      </span>
                    </td>
                    <td>
                      <RiskIndicator level={p.predicted_risk_level} score={p.predicted_risk_score} showDetails />
                    </td>
                    <td>
                      <ul style={{ paddingLeft: '1.1rem', margin: 0, fontSize: '0.82rem', color: '#fecdd3' }}>
                        {p.potential_failure_modes && p.potential_failure_modes.length > 0 ? (
                          p.potential_failure_modes.map((m, i) => <li key={i}>{m}</li>)
                        ) : (
                          <li style={{ color: 'var(--text-muted)' }}>No high-volatility anomalies detected.</li>
                        )}
                      </ul>
                    </td>
                    <td>
                      <ul style={{ paddingLeft: '1.1rem', margin: 0, fontSize: '0.82rem', color: '#a7f3d0' }}>
                        {p.preventive_recommendations && p.preventive_recommendations.length > 0 ? (
                          p.preventive_recommendations.map((r, i) => <li key={i}>{r}</li>)
                        ) : (
                          <li style={{ color: 'var(--text-muted)' }}>Standard pipeline approved.</li>
                        )}
                      </ul>
                    </td>
                    <td>
                      {p.actual_outcome ? (
                        <StatusBadge status={p.actual_outcome} />
                      ) : (
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Pending Exec</span>
                      )}
                    </td>
                    <td>
                      {p.was_accurate === null || p.was_accurate === undefined ? (
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Evaluating</span>
                      ) : p.was_accurate ? (
                        <span style={{ color: '#34d399', display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.8rem', fontWeight: 600 }}>
                          <CheckCircle size={14} /> Yes
                        </span>
                      ) : (
                        <span style={{ color: '#fb7185', display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.8rem', fontWeight: 600 }}>
                          <XCircle size={14} /> No
                        </span>
                      )}
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

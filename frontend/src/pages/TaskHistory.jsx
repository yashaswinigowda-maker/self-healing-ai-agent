import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import StatusBadge from '../components/StatusBadge';
import RiskIndicator from '../components/RiskIndicator';
import {
  History,
  Search,
  RefreshCw,
  ExternalLink,
  X,
  CheckCircle,
  AlertTriangle,
  Sparkles,
  FileText,
} from 'lucide-react';

export default function TaskHistory({ selectedTaskId, setSelectedTaskId }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');

  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.listTasks(filterStatus === 'ALL' ? null : filterStatus);
      setTasks(data);

      if (selectedTaskId) {
        loadTaskDetails(selectedTaskId);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadTaskDetails = async (id) => {
    try {
      setLoadingDetails(true);
      const data = await api.getTaskDetails(id);
      setSelectedTask(data);
    } catch (err) {
      console.error('Failed to load task details:', err);
    } finally {
      setLoadingDetails(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, [filterStatus]);

  useEffect(() => {
    if (selectedTaskId) {
      loadTaskDetails(selectedTaskId);
    }
  }, [selectedTaskId]);

  const filteredTasks = tasks.filter((t) => {
    if (!searchTerm.trim()) return true;
    const q = searchTerm.toLowerCase();
    return t.title.toLowerCase().includes(q) || t.description.toLowerCase().includes(q) || t.id.toLowerCase().includes(q);
  });

  return (
    <div className="page-wrapper">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff' }}>Automation Task History</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Comprehensive audit log of multi-step task executions, self-healing events, verification scores, and replans.
          </p>
        </div>

        <button onClick={fetchTasks} className="btn btn-secondary" style={{ fontSize: '0.85rem' }}>
          <RefreshCw size={14} className={loading ? 'spin-animate' : ''} />
          <span>Refresh History</span>
        </button>
      </div>

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: '8px', color: '#fb7185', marginBottom: '1.5rem' }}>
          {error}
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="glass-card" style={{ marginBottom: '1.5rem', padding: '1rem 1.25rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Filter Status:</span>
          {['ALL', 'COMPLETED', 'RECOVERED', 'FAILED', 'RUNNING'].map((st) => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              className="btn btn-secondary"
              style={{
                fontSize: '0.78rem',
                padding: '0.3rem 0.65rem',
                borderRadius: '6px',
                background: filterStatus === st ? 'rgba(99, 102, 241, 0.2)' : 'transparent',
                borderColor: filterStatus === st ? 'var(--accent-indigo)' : 'var(--border-subtle)',
                color: filterStatus === st ? '#fff' : 'var(--text-secondary)',
              }}
            >
              {st}
            </button>
          ))}
        </div>

        <div style={{ position: 'relative', width: '280px' }}>
          <Search size={15} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search tasks..."
            className="input-field"
            style={{ paddingLeft: '2rem', padding: '0.4rem 0.6rem 0.4rem 2rem', fontSize: '0.85rem' }}
          />
        </div>
      </div>

      {/* Tasks Table */}
      <div className="glass-card">
        {loading && tasks.length === 0 ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '40vh' }}>
            <RefreshCw size={28} className="spin-animate" color="var(--accent-indigo)" />
          </div>
        ) : filteredTasks.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
            No task records found matching your filter.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Task Title</th>
                  <th>Status</th>
                  <th>Steps</th>
                  <th>Recoveries</th>
                  <th>Replans</th>
                  <th>Confidence</th>
                  <th>Pre-Risk</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredTasks.map((t) => (
                  <tr key={t.id}>
                    <td>
                      <div style={{ fontWeight: 600, color: '#fff' }}>{t.title}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {t.id.substring(0, 8)}... | {new Date(t.created_at).toLocaleString()}
                      </div>
                    </td>
                    <td>
                      <StatusBadge status={t.status} />
                    </td>
                    <td>{t.successful_steps}/{t.total_steps}</td>
                    <td>
                      {t.recovery_attempts_count > 0 ? (
                        <span style={{ color: 'var(--accent-indigo)', fontWeight: 700 }}>
                          ⚡ {t.recovery_attempts_count}
                        </span>
                      ) : (
                        <span style={{ color: 'var(--text-muted)' }}>0</span>
                      )}
                    </td>
                    <td>{t.replan_count}</td>
                    <td>
                      <span className="font-mono" style={{ color: t.final_confidence >= 0.7 ? '#34d399' : '#fbbf24', fontWeight: 600 }}>
                        {(t.final_confidence * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td>
                      <RiskIndicator level={t.predicted_risk_level} />
                    </td>
                    <td>
                      <button
                        onClick={() => loadTaskDetails(t.id)}
                        className="btn btn-secondary"
                        style={{ padding: '0.3rem 0.65rem', fontSize: '0.78rem' }}
                      >
                        Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Task Details Modal / Drawer */}
      {selectedTask && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            right: 0,
            bottom: 0,
            width: '600px',
            maxWidth: '90vw',
            background: 'var(--bg-secondary)',
            borderLeft: '1px solid var(--border-subtle)',
            boxShadow: '-10px 0 30px rgba(0, 0, 0, 0.7)',
            zIndex: 100,
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {/* Modal Header */}
          <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>Task Audit Details</h3>
              <p className="font-mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{selectedTask.id}</p>
            </div>
            <button
              onClick={() => {
                setSelectedTask(null);
                if (setSelectedTaskId) setSelectedTaskId(null);
              }}
              className="btn btn-secondary"
              style={{ padding: '0.35rem', borderRadius: '50%' }}
            >
              <X size={16} />
            </button>
          </div>

          {/* Modal Body */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div>
              <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#fff', marginBottom: '0.3rem' }}>{selectedTask.title}</h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{selectedTask.description}</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', background: 'var(--bg-input)', padding: '1rem', borderRadius: '8px' }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Execution Status</span>
                <div><StatusBadge status={selectedTask.status} /></div>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Final Confidence Score</span>
                <div className="font-mono" style={{ fontWeight: 700, color: '#34d399' }}>
                  {(selectedTask.final_confidence * 100).toFixed(0)}%
                </div>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Self-Healing Recoveries</span>
                <div style={{ fontWeight: 600, color: '#fff' }}>{selectedTask.recovery_attempts_count}</div>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Dynamic Replans</span>
                <div style={{ fontWeight: 600, color: '#fff' }}>{selectedTask.replan_count}</div>
              </div>
            </div>

            {/* Steps Sequence */}
            <div>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                Executed Steps ({selectedTask.steps.length})
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {selectedTask.steps.map((st, idx) => (
                  <div key={st.id || idx} style={{ padding: '0.75rem 1rem', background: 'var(--bg-card)', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                      <span style={{ fontWeight: 600, fontSize: '0.85rem', color: '#fff' }}>
                        {idx + 1}. {st.step_name} {st.is_replacement && <span style={{ color: 'var(--accent-indigo)', fontSize: '0.75rem' }}>(Replaced)</span>}
                      </span>
                      <StatusBadge status={st.status} />
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                      Tool: {st.tool_name}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Final Output */}
            {selectedTask.final_output && (
              <div>
                <h4 style={{ fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                  Final Result Payload
                </h4>
                <div className="font-mono" style={{ padding: '0.85rem', background: 'var(--bg-input)', borderRadius: '6px', fontSize: '0.8rem', color: '#34d399', whiteSpace: 'pre-wrap' }}>
                  {selectedTask.final_output}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

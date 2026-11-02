import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import StatusBadge from '../components/StatusBadge';
import {
  Brain,
  Search,
  CheckCircle,
  XCircle,
  Sparkles,
  RefreshCw,
  Tag,
  Repeat,
  Zap,
} from 'lucide-react';

export default function MemoryManagement() {
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedType, setSelectedType] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchMemories = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getMemories(
        selectedType === 'ALL' ? null : selectedType,
        searchQuery.trim() || null
      );
      setMemories(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMemories();
  }, [selectedType]);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchMemories();
  };

  return (
    <div className="page-wrapper">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff' }}>Episodic Memory Management</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Persistent failure and success catalog used to avoid repeating previously failed recovery actions and inject relevant context into Gemini.
          </p>
        </div>

        <button onClick={fetchMemories} className="btn btn-secondary" style={{ fontSize: '0.85rem' }}>
          <RefreshCw size={14} className={loading ? 'spin-animate' : ''} />
          <span>Refresh Memory</span>
        </button>
      </div>

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: '8px', color: '#fb7185', marginBottom: '1.5rem' }}>
          {error}
        </div>
      )}

      {/* Search & Filter Bar */}
      <div className="glass-card" style={{ marginBottom: '1.5rem', padding: '1rem 1.25rem' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ position: 'relative', flex: 1, minWidth: '240px' }}>
            <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search experiences by error, tool, or recovery strategy..."
              className="input-field"
              style={{ paddingLeft: '2.25rem' }}
            />
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            {['ALL', 'SUCCESS', 'FAILURE'].map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setSelectedType(t)}
                className="btn btn-secondary"
                style={{
                  fontSize: '0.8rem',
                  padding: '0.4rem 0.8rem',
                  borderRadius: '6px',
                  background: selectedType === t ? 'rgba(99, 102, 241, 0.2)' : 'transparent',
                  borderColor: selectedType === t ? 'var(--accent-indigo)' : 'var(--border-subtle)',
                  color: selectedType === t ? '#fff' : 'var(--text-secondary)',
                }}
              >
                {t === 'SUCCESS' ? '✓ Successful' : t === 'FAILURE' ? '✕ Failed' : 'All Memories'}
              </button>
            ))}
          </div>

          <button type="submit" className="btn btn-primary" style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}>
            Search
          </button>
        </form>
      </div>

      {/* Memory Cards Grid */}
      {loading && memories.length === 0 ? (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '40vh' }}>
          <RefreshCw size={28} className="spin-animate" color="var(--accent-indigo)" />
        </div>
      ) : memories.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
          No episodic memories found matching your criteria.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(420px, 1fr))', gap: '1.25rem' }}>
          {memories.map((mem) => {
            const isSuccess = mem.memory_type === 'SUCCESS';
            return (
              <div
                key={mem.id}
                className="glass-card"
                style={{
                  borderTop: isSuccess ? '3px solid #10b981' : '3px solid #f43f5e',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      {isSuccess ? <CheckCircle size={16} color="#10b981" /> : <XCircle size={16} color="#f43f5e" />}
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: isSuccess ? '#34d399' : '#fb7185', textTransform: 'uppercase' }}>
                        {isSuccess ? 'Validated Healing Pattern' : 'Known Failed Strategy'}
                      </span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      <Repeat size={12} />
                      <span>Freq: {mem.frequency}</span>
                    </div>
                  </div>

                  <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#fff', marginBottom: '0.35rem' }}>
                    {mem.task_description}
                  </h3>

                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
                    Tool: <span className="font-mono" style={{ color: '#cbd5e1' }}>{mem.tool_name}</span> | Error: <span style={{ color: '#fb7185' }}>{mem.error_category || 'Fault'}</span>
                  </div>

                  {mem.error_message && (
                    <div style={{ padding: '0.5rem 0.75rem', background: 'rgba(0, 0, 0, 0.3)', borderRadius: '6px', fontSize: '0.8rem', color: '#fecdd3', marginBottom: '0.75rem' }}>
                      "{mem.error_message}"
                    </div>
                  )}

                  {mem.diagnosis && (
                    <div style={{ fontSize: '0.82rem', color: '#e2e8f0', marginBottom: '0.75rem' }}>
                      <strong style={{ color: '#818cf8' }}>Learned Diagnosis: </strong>
                      {mem.diagnosis}
                    </div>
                  )}

                  {mem.recovery_strategy && (
                    <div style={{ padding: '0.6rem 0.8rem', background: isSuccess ? 'rgba(16, 185, 129, 0.1)' : 'rgba(244, 63, 94, 0.1)', borderRadius: '6px', fontSize: '0.82rem', marginBottom: '0.75rem' }}>
                      <div style={{ fontWeight: 600, color: isSuccess ? '#34d399' : '#fb7185', marginBottom: '0.2rem' }}>
                        Strategy: {mem.recovery_strategy}
                      </div>
                      <div className="font-mono" style={{ fontSize: '0.75rem', color: '#e2e8f0' }}>
                        {JSON.stringify(mem.recovery_action)}
                      </div>
                    </div>
                  )}
                </div>

                {/* Footer Tags & Score */}
                <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '0.75rem', marginTop: '0.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
                    {mem.tags?.map((t, idx) => (
                      <span key={idx} style={{ padding: '0.15rem 0.4rem', borderRadius: '4px', background: 'var(--bg-input)', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                        #{t}
                      </span>
                    ))}
                  </div>

                  <span className="font-mono" style={{ fontSize: '0.8rem', color: '#a5b4fc', fontWeight: 600 }}>
                    Confidence: {(mem.confidence_score * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

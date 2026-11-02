import React, { useState } from 'react';
import { api } from '../api/client';
import StatusBadge from '../components/StatusBadge';
import RiskIndicator from '../components/RiskIndicator';
import {
  Play,
  RotateCcw,
  Sparkles,
  AlertTriangle,
  CheckCircle,
  HelpCircle,
  Zap,
  ArrowRight,
  ShieldCheck,
  FileText,
  Clock,
} from 'lucide-react';

const PRESETS = [
  {
    title: 'Calculate ROI with Arithmetic Fault (Auto-Healed)',
    description: 'Calculate annual revenue growth and return on investment with arithmetic divisor calculation.',
    fault: 'division_by_zero',
  },
  {
    title: 'Query Service with Dynamic Failover Re-planning',
    description: 'Query remote legacy service gateway, extract system records, and persist backup summary artifact.',
    fault: 'service_unavailable',
  },
  {
    title: 'Research Autonomous Self-Healing AI Paradigms',
    description: 'Search latest AI agent self-healing papers, summarize reliability benchmarks, and output report.',
    fault: null,
  },
  {
    title: 'Fetch & Validate Multi-City Meteorological Data',
    description: 'Fetch current weather observations for Seattle, format temperature metrics, and save to sandbox storage.',
    fault: null,
  },
];

export default function TaskExecution({ setActivePage, setSelectedTaskId }) {
  const [title, setTitle] = useState(PRESETS[0].title);
  const [description, setDescription] = useState(PRESETS[0].description);
  const [forceFault, setForceFault] = useState(PRESETS[0].fault || '');

  const [isPlanning, setIsPlanning] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [currentTask, setCurrentTask] = useState(null);
  const [error, setError] = useState(null);

  const applyPreset = (p) => {
    setTitle(p.title);
    setDescription(p.description);
    setForceFault(p.fault || '');
  };

  const handlePlanAndRun = async () => {
    if (!description.trim() || !title.trim()) {
      setError('Please provide a task title and description.');
      return;
    }

    try {
      setError(null);
      setIsPlanning(true);
      setCurrentTask(null);

      // 1. Create and plan task with Gemini
      const task = await api.createTask(title, description, forceFault || null);
      setCurrentTask(task);
      setIsPlanning(false);

      // 2. Automatically execute task
      setIsExecuting(true);
      const executedTask = await api.executeTask(task.id);
      setCurrentTask(executedTask);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsPlanning(false);
      setIsExecuting(false);
    }
  };

  return (
    <div className="page-wrapper">
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff' }}>Task Planning & Execution Engine</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Decomposes complex requests into discrete verifiable steps with autonomous self-healing, dynamic re-planning, and error adaptation.
        </p>
      </div>

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: '8px', color: '#fb7185', marginBottom: '1.5rem' }}>
          {error}
        </div>
      )}

      {/* Task Input Section */}
      <div className="glass-card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>1. Enter Automation Task</h3>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Quick Presets:</span>
        </div>

        {/* Quick Presets Pills */}
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1.25rem' }}>
          {PRESETS.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => applyPreset(p)}
              className="btn btn-secondary"
              style={{
                fontSize: '0.78rem',
                padding: '0.35rem 0.75rem',
                borderRadius: '6px',
                borderColor: title === p.title ? 'var(--accent-indigo)' : 'var(--border-subtle)',
                background: title === p.title ? 'rgba(99, 102, 241, 0.15)' : 'var(--bg-input)',
              }}
            >
              {p.fault ? '⚡ ' : '✓ '} {p.title.split(' ')[0]} {p.title.split(' ')[1]}
            </button>
          ))}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              Task Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="input-field"
              placeholder="e.g. Calculate profit and ROI"
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              Fault Injection Simulator (Optional Demo)
            </label>
            <select
              value={forceFault}
              onChange={(e) => setForceFault(e.target.value)}
              className="select-field"
            >
              <option value="">No Injected Fault (Clean Run)</option>
              <option value="division_by_zero">Parameter Fault (Division by Zero)</option>
              <option value="service_unavailable">Service Fault (503 Unavailable - Replan)</option>
              <option value="network_timeout">Transient Network Latency (Auto-Retry)</option>
            </select>
          </div>
        </div>

        <div style={{ marginBottom: '1.25rem' }}>
          <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
            Multi-Step Task Description
          </label>
          <textarea
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="textarea-field"
            placeholder="Describe the end goal of the multi-step task..."
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
          <button
            onClick={handlePlanAndRun}
            disabled={isPlanning || isExecuting}
            className="btn btn-primary"
            style={{ padding: '0.75rem 2rem' }}
          >
            {isPlanning ? (
              <>
                <RotateCcw size={16} className="spin-animate" />
                <span>Decomposing Plan with Gemini...</span>
              </>
            ) : isExecuting ? (
              <>
                <Zap size={16} className="spin-animate" />
                <span>Self-Healing Engine Executing...</span>
              </>
            ) : (
              <>
                <Play size={16} />
                <span>Plan & Execute Task</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Live Execution Output & Steps Timeline */}
      {currentTask && (
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff' }}>{currentTask.title}</h3>
                <StatusBadge status={currentTask.status} />
              </div>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                Task ID: <span className="font-mono">{currentTask.id}</span>
              </p>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Failure Risk</div>
                <RiskIndicator level={currentTask.predicted_risk_level} score={currentTask.predictions?.[0]?.predicted_risk_score || 0.15} showDetails />
              </div>

              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Final Confidence</div>
                <div className="font-mono" style={{ fontSize: '1.1rem', fontWeight: 700, color: currentTask.final_confidence >= 0.7 ? '#34d399' : '#fbbf24' }}>
                  {(currentTask.final_confidence * 100).toFixed(0)}%
                </div>
              </div>
            </div>
          </div>

          {/* Steps Timeline Display */}
          <div style={{ marginBottom: '2rem' }}>
            <h4 style={{ fontSize: '0.9rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '1rem' }}>
              Step-by-Step Execution Sequence
            </h4>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {currentTask.steps.map((step, idx) => {
                const isReplacement = step.is_replacement;
                const verif = currentTask.verifications?.find((v) => v.step_id === step.id);
                const rec = currentTask.recovery_attempts?.find((r) => r.step_id === step.id);

                return (
                  <div
                    key={step.id || idx}
                    style={{
                      padding: '1.25rem',
                      background: isReplacement ? 'rgba(99, 102, 241, 0.08)' : 'var(--bg-input)',
                      border: isReplacement ? '1px dashed var(--accent-indigo)' : '1px solid var(--border-subtle)',
                      borderRadius: '10px',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <span
                          style={{
                            width: '28px',
                            height: '28px',
                            borderRadius: '50%',
                            background: step.status === 'COMPLETED' ? 'rgba(16, 185, 129, 0.2)' : step.status === 'RECOVERED' ? 'rgba(99, 102, 241, 0.2)' : 'rgba(244, 63, 94, 0.2)',
                            color: step.status === 'COMPLETED' ? '#34d399' : step.status === 'RECOVERED' ? '#818cf8' : '#fb7185',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontWeight: 700,
                            fontSize: '0.8rem',
                          }}
                        >
                          {idx + 1}
                        </span>
                        <div>
                          <div style={{ fontWeight: 600, color: '#fff', fontSize: '0.95rem' }}>
                            {step.step_name} {isReplacement && <span style={{ color: 'var(--accent-indigo)', fontSize: '0.75rem' }}>(Dynamic Replacement)</span>}
                          </div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                            Tool: {step.tool_name}
                          </div>
                        </div>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        {verif && (
                          <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                            Heuristic: <strong>{(verif.heuristic_score * 100).toFixed(0)}%</strong> | Calibrated: <strong>{(verif.calibrated_probability * 100).toFixed(0)}%</strong>
                          </span>
                        )}
                        <StatusBadge status={step.status} />
                      </div>
                    </div>

                    {/* Step Arguments */}
                    <div style={{ fontSize: '0.8rem', background: 'rgba(0, 0, 0, 0.25)', padding: '0.5rem 0.75rem', borderRadius: '6px', marginBottom: '0.5rem' }}>
                      <span style={{ color: 'var(--text-muted)' }}>Arguments: </span>
                      <span className="font-mono" style={{ color: '#e2e8f0' }}>{JSON.stringify(step.tool_arguments)}</span>
                    </div>

                    {/* If step triggered recovery */}
                    {rec && (
                      <div style={{ marginTop: '0.75rem', padding: '0.75rem', background: 'rgba(99, 102, 241, 0.12)', borderLeft: '3px solid var(--accent-indigo)', borderRadius: '4px' }}>
                        <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#a5b4fc', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                          <Sparkles size={14} />
                          <span>Self-Healing Diagnosis & Action</span>
                        </div>
                        <div style={{ fontSize: '0.8rem', color: '#cbd5e1', marginTop: '0.25rem' }}>
                          <strong>Fault Detected:</strong> {rec.error_detected}
                        </div>
                        <div style={{ fontSize: '0.8rem', color: '#cbd5e1', marginTop: '0.2rem' }}>
                          <strong>Root Cause:</strong> {rec.diagnosis}
                        </div>
                        <div style={{ fontSize: '0.8rem', color: '#a5b4fc', marginTop: '0.2rem' }}>
                          <strong>Strategy Selected:</strong> {rec.selected_strategy} (Safety Validation: {rec.is_validated ? 'APPROVED' : 'REJECTED'})
                        </div>
                      </div>
                    )}

                    {/* Output Preview */}
                    {step.output && (
                      <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                        <span style={{ color: '#34d399', fontWeight: 600 }}>Output: </span>
                        <span className="font-mono">{typeof step.output === 'object' ? JSON.stringify(step.output).substring(0, 160) : String(step.output).substring(0, 160)}...</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Final Output Summary Card */}
          <div style={{ padding: '1.25rem', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.25)', borderRadius: '8px' }}>
            <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#34d399', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <CheckCircle size={16} />
              <span>Final Execution Summary</span>
            </h4>
            <p style={{ fontSize: '0.88rem', color: '#e2e8f0' }}>{currentTask.final_output}</p>
          </div>
        </div>
      )}
    </div>
  );
}

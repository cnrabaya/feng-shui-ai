// ─────────────────────────────────────────────
// StepIndicator.jsx
// Shows current flow step: Upload → Analysis → Layouts
// ─────────────────────────────────────────────
import React from 'react';

const STEPS = [
  { id: 1, label: 'Upload Room',   icon: '⬆' },
  { id: 2, label: 'AI Analysis',   icon: '◎' },
  { id: 3, label: 'Feng Shui',     icon: '☯' },
  { id: 4, label: 'Layouts',       icon: '⊞' },
];

export default function StepIndicator({ currentStep = 1 }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 0, padding: '0 var(--space-4)' }}>
      {STEPS.map((step, i) => {
        const isActive   = step.id === currentStep;
        const isComplete = step.id < currentStep;
        return (
          <React.Fragment key={step.id}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 'var(--space-2)' }}>
              <div style={{
                width: 36, height: 36, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 'var(--text-sm)',
                background: isComplete ? 'var(--gold-soft)' : isActive ? 'var(--gold-bright)' : 'var(--bg-raised)',
                color: (isComplete || isActive) ? 'var(--ink-900)' : 'var(--text-muted)',
                border: isActive ? '2px solid var(--gold-bright)' : '2px solid transparent',
                boxShadow: isActive ? '0 0 12px var(--gold-glow)' : 'none',
                transition: 'all var(--duration-normal) var(--ease-smooth)',
                fontWeight: isActive ? 700 : 400,
              }}>
                {isComplete ? '✓' : step.icon}
              </div>
              <span style={{
                fontSize: 'var(--text-xs)', fontFamily: 'var(--font-body)',
                color: isActive ? 'var(--gold-bright)' : isComplete ? 'var(--text-secondary)' : 'var(--text-muted)',
                whiteSpace: 'nowrap', letterSpacing: '0.05em',
                transition: 'color var(--duration-normal)',
              }}>
                {step.label}
              </span>
            </div>
            {i < STEPS.length - 1 && (
              <div style={{
                flex: 1, height: 1, minWidth: 32,
                background: isComplete ? 'var(--gold-muted)' : 'var(--border-subtle)',
                margin: '-18px var(--space-3) 0',
                transition: 'background var(--duration-slow)',
              }} />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}

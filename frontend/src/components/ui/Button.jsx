// ─────────────────────────────────────────────
// Button.jsx — Shared primitive
// ─────────────────────────────────────────────
import React from 'react';

const VARIANTS = {
  primary:   { background: 'var(--gold-bright)', color: 'var(--ink-900)', border: 'none', fontWeight: 600 },
  secondary: { background: 'transparent', color: 'var(--gold-bright)', border: '1px solid var(--border-default)', fontWeight: 400 },
  ghost:     { background: 'transparent', color: 'var(--text-secondary)', border: '1px solid var(--border-subtle)', fontWeight: 400 },
  danger:    { background: 'transparent', color: 'var(--red-accent)', border: '1px solid rgba(192,57,43,0.4)', fontWeight: 400 },
};
const SIZES = {
  sm: { padding: '6px 14px',  fontSize: 'var(--text-sm)',   borderRadius: 'var(--radius-sm)' },
  md: { padding: '10px 20px', fontSize: 'var(--text-base)', borderRadius: 'var(--radius-md)' },
  lg: { padding: '14px 28px', fontSize: 'var(--text-lg)',   borderRadius: 'var(--radius-md)' },
};

export default function Button({ children, variant = 'primary', size = 'md', disabled = false, fullWidth = false, onClick, style = {}, ...props }) {
  const v = VARIANTS[variant] || VARIANTS.primary;
  const s = SIZES[size] || SIZES.md;
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
        cursor: disabled ? 'not-allowed' : 'pointer', opacity: disabled ? 0.45 : 1,
        transition: `all var(--duration-normal) var(--ease-smooth)`,
        fontFamily: 'var(--font-body)', letterSpacing: '0.01em',
        width: fullWidth ? '100%' : 'auto', ...v, ...s, ...style }}
      onMouseEnter={e => { if (!disabled) { e.currentTarget.style.opacity = '0.85'; e.currentTarget.style.transform = 'translateY(-1px)'; }}}
      onMouseLeave={e => { e.currentTarget.style.opacity = '1'; e.currentTarget.style.transform = 'translateY(0)'; }}
      {...props}
    >
      {children}
    </button>
  );
}

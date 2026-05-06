import React from 'react';
export default function Card({ children, style = {}, highlight = false, onClick, ...props }) {
  return (
    <div onClick={onClick}
      style={{ background:'var(--bg-surface)', border: highlight?'1px solid var(--border-strong)':'1px solid var(--border-subtle)',
        borderRadius:'var(--radius-lg)', padding:'var(--space-6)', boxShadow: highlight?'var(--shadow-gold)':'var(--shadow-sm)',
        transition:'border-color var(--duration-normal), box-shadow var(--duration-normal)',
        cursor: onClick?'pointer':'default', ...style }} {...props}>
      {children}
    </div>
  );
}

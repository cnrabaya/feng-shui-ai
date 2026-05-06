import React, { useEffect, useState } from 'react';
const MESSAGES = ['Reading the room\'s energy…','Mapping the qi flow…','Consulting the bagua…','Weighing the five elements…','Calculating harmony score…','Designing alternatives…'];
export default function LoadingState({ message = '' }) {
  const [msgIndex, setMsgIndex] = useState(0);
  const [fade, setFade] = useState(true);
  useEffect(() => {
    const interval = setInterval(() => {
      setFade(false);
      setTimeout(() => { setMsgIndex(prev => (prev + 1) % MESSAGES.length); setFade(true); }, 300);
    }, 2400);
    return () => clearInterval(interval);
  }, []);
  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:'var(--space-8)', padding:'var(--space-16) var(--space-8)', minHeight:320 }}>
      <div style={{ position:'relative', width:80, height:80 }}>
        <svg width="80" height="80" viewBox="0 0 80 80" style={{ animation:'spin 8s linear infinite' }}>
          <style>{`@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}`}</style>
          <circle cx="40" cy="40" r="36" fill="none" stroke="var(--border-subtle)" strokeWidth="1"/>
          <circle cx="40" cy="40" r="36" fill="none" stroke="var(--gold-bright)" strokeWidth="2" strokeDasharray="56 170" strokeLinecap="round"/>
        </svg>
        <div style={{ position:'absolute', inset:0, display:'flex', alignItems:'center', justifyContent:'center', fontSize:28, animation:'pulse 2s ease-in-out infinite' }}>
          <style>{`@keyframes pulse{0%,100%{opacity:0.6;transform:scale(0.95)}50%{opacity:1;transform:scale(1.05)}}`}</style>
          ☯
        </div>
      </div>
      <div style={{ textAlign:'center' }}>
        <p style={{ fontFamily:'var(--font-display)', fontSize:'var(--text-lg)', color:'var(--gold-bright)', letterSpacing:'0.02em', opacity:fade?1:0, transition:'opacity 0.3s ease', minHeight:'1.8em' }}>
          {message || MESSAGES[msgIndex]}
        </p>
        <p style={{ color:'var(--text-muted)', fontSize:'var(--text-sm)', marginTop:'var(--space-2)' }}>This may take a moment</p>
      </div>
      <div style={{ display:'flex', gap:'var(--space-2)' }}>
        {[0,1,2].map(i=>(
          <div key={i} style={{ width:6, height:6, borderRadius:'50%', background:'var(--gold-muted)', animation:`bounce 1.2s ${i*0.2}s ease-in-out infinite` }}>
            <style>{`@keyframes bounce{0%,80%,100%{transform:scale(0.6);opacity:0.4}40%{transform:scale(1);opacity:1}}`}</style>
          </div>
        ))}
      </div>
    </div>
  );
}

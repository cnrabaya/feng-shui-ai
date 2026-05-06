// ImageUploader.jsx — Drag-and-drop + click-to-upload room image
import React, { useState, useRef, useCallback } from 'react';

export default function ImageUploader({ onImageReady }) {
  const [preview, setPreview]   = useState(null);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);

  const processFile = useCallback((file) => {
    if (!file || !file.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      const dataUrl = e.target.result;
      setPreview(dataUrl);
      onImageReady({ base64: dataUrl.split(',')[1], mediaType: file.type, file });
    };
    reader.readAsDataURL(file);
  }, [onImageReady]);

  const handleDrop = useCallback((e) => {
    e.preventDefault(); setDragging(false);
    processFile(e.dataTransfer.files[0]);
  }, [processFile]);

  return (
    <div
      style={{
        display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center',
        gap:'var(--space-4)', padding:'var(--space-10)',
        border:`2px dashed ${dragging?'var(--gold-bright)':'var(--border-default)'}`,
        borderRadius:'var(--radius-xl)',
        background: dragging?'var(--gold-glow)':'var(--bg-raised)',
        cursor:'pointer', minHeight:220,
        transition:'all var(--duration-normal) var(--ease-smooth)',
        boxShadow: dragging?'var(--shadow-gold)':'none',
      }}
      onDragOver={e=>{e.preventDefault();setDragging(true);}}
      onDragLeave={()=>setDragging(false)}
      onDrop={handleDrop}
      onClick={()=>inputRef.current?.click()}
    >
      <input ref={inputRef} type="file" accept="image/*" style={{display:'none'}} onChange={e=>processFile(e.target.files[0])}/>
      {preview ? (
        <>
          <img src={preview} alt="Room preview" style={{maxHeight:200,maxWidth:'100%',borderRadius:'var(--radius-md)',objectFit:'contain'}}/>
          <p style={{color:'var(--gold-bright)',fontSize:'var(--text-sm)'}}>Click or drop to change image</p>
        </>
      ) : (
        <>
          <div style={{fontSize:48,opacity:0.6}}>⬆</div>
          <div style={{textAlign:'center'}}>
            <p style={{fontFamily:'var(--font-display)',fontSize:'var(--text-lg)',color:'var(--text-primary)',marginBottom:'var(--space-2)'}}>Drop a room photo here</p>
            <p style={{color:'var(--text-muted)',fontSize:'var(--text-sm)'}}>or click to browse · JPG, PNG, WEBP</p>
          </div>
        </>
      )}
    </div>
  );
}

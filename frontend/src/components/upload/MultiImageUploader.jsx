// ─────────────────────────────────────────────
// MultiImageUploader.jsx
// Replaces ImageUploader. Supports multiple photos,
// each with its own OrientationPicker.
// ─────────────────────────────────────────────
import React, { useRef, useCallback } from 'react';
import OrientationPicker from './OrientationPicker';
import Button from '../ui/Button';

function PhotoCard({ photo, index, onRemove, onOrientationChange, isPrimary }) {
  return (
    <div style={{
      background: 'var(--bg-raised)',
      border: `1px solid ${isPrimary ? 'var(--border-strong)' : 'var(--border-subtle)'}`,
      borderRadius: 'var(--radius-lg)',
      overflow: 'hidden',
      transition: 'border-color var(--duration-normal)',
    }}>
      {/* Image preview header */}
      <div style={{ position: 'relative' }}>
        <img
          src={photo.previewUrl}
          alt={`Room photo ${index + 1}`}
          style={{ width: '100%', height: 160, objectFit: 'cover', display: 'block' }}
        />
        {/* Badges */}
        <div style={{ position: 'absolute', top: 8, left: 8, display: 'flex', gap: 6 }}>
          {isPrimary && (
            <span style={{
              background: 'var(--gold-bright)', color: 'var(--ink-900)',
              fontSize: 'var(--text-xs)', fontWeight: 700,
              padding: '2px 8px', borderRadius: 'var(--radius-sm)', letterSpacing: '0.06em',
            }}>PRIMARY</span>
          )}
          {photo.orientation && (
            <span style={{
              background: 'rgba(0,0,0,0.6)', color: 'var(--gold-bright)',
              fontSize: 'var(--text-xs)', fontWeight: 600,
              padding: '2px 8px', borderRadius: 'var(--radius-sm)',
              backdropFilter: 'blur(4px)',
            }}>↑ {photo.orientation}</span>
          )}
        </div>
        {/* Remove button */}
        <button
          onClick={() => onRemove(photo.id)}
          style={{
            position: 'absolute', top: 8, right: 8,
            background: 'rgba(0,0,0,0.6)', border: 'none', borderRadius: '50%',
            width: 28, height: 28, cursor: 'pointer', color: 'var(--text-primary)',
            fontSize: 14, display: 'flex', alignItems: 'center', justifyContent: 'center',
            backdropFilter: 'blur(4px)',
          }}
        >✕</button>
      </div>

      {/* Orientation picker */}
      <div style={{ padding: 'var(--space-4)' }}>
        <p style={{
          color: 'var(--text-muted)', fontSize: 'var(--text-xs)',
          letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 'var(--space-3)',
        }}>
          Photo {index + 1} — Facing Direction
        </p>
        <OrientationPicker
          value={photo.orientation}
          onChange={(dir) => onOrientationChange(photo.id, dir)}
          compact
        />
      </div>
    </div>
  );
}

export default function MultiImageUploader({ photos = [], onPhotosChange }) {
  const inputRef = useRef(null);

  const processFiles = useCallback((files) => {
    const newPhotos = Array.from(files)
      .filter(f => f.type.startsWith('image/'))
      .map(file => {
        const id = `photo_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
        const previewUrl = URL.createObjectURL(file);
        return new Promise(resolve => {
          const reader = new FileReader();
          reader.onload = (e) => {
            resolve({
              id,
              file,
              previewUrl,
              base64: e.target.result.split(',')[1],
              mediaType: file.type,
              orientation: null,
            });
          };
          reader.readAsDataURL(file);
        });
      });

    Promise.all(newPhotos).then(resolved => {
      onPhotosChange([...photos, ...resolved]);
    });
  }, [photos, onPhotosChange]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    processFiles(e.dataTransfer.files);
  }, [processFiles]);

  const handleRemove = useCallback((id) => {
    onPhotosChange(photos.filter(p => p.id !== id));
  }, [photos, onPhotosChange]);

  const handleOrientationChange = useCallback((id, direction) => {
    onPhotosChange(photos.map(p => p.id === id ? { ...p, orientation: direction } : p));
  }, [photos, onPhotosChange]);

  const hasPhotos = photos.length > 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>

      {/* Drop zone */}
      <div
        onDragOver={e => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        style={{
          border: '2px dashed var(--border-default)',
          borderRadius: 'var(--radius-xl)',
          padding: hasPhotos ? 'var(--space-4)' : 'var(--space-10)',
          background: 'var(--bg-raised)',
          cursor: 'pointer',
          textAlign: 'center',
          transition: 'all var(--duration-normal)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          gap: 'var(--space-4)',
          minHeight: hasPhotos ? 72 : 180,
        }}
        onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--gold-bright)'}
        onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border-default)'}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          multiple
          style={{ display: 'none' }}
          onChange={e => processFiles(e.target.files)}
        />
        <span style={{ fontSize: hasPhotos ? 20 : 40, opacity: 0.5 }}>⬆</span>
        <div>
          <p style={{ color: 'var(--text-primary)', fontSize: hasPhotos ? 'var(--text-sm)' : 'var(--text-lg)', fontFamily: 'var(--font-display)' }}>
            {hasPhotos ? 'Add more photos' : 'Drop room photos here'}
          </p>
          {!hasPhotos && (
            <p style={{ color: 'var(--text-muted)', fontSize: 'var(--text-sm)', marginTop: 4 }}>
              Add multiple photos from different angles · JPG, PNG, WEBP
            </p>
          )}
        </div>
      </div>

      {/* Photo cards grid */}
      {hasPhotos && (
        <>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
            gap: 'var(--space-4)',
          }}>
            {photos.map((photo, i) => (
              <PhotoCard
                key={photo.id}
                photo={photo}
                index={i}
                isPrimary={i === 0}
                onRemove={handleRemove}
                onOrientationChange={handleOrientationChange}
              />
            ))}
          </div>

          {/* Orientation coverage summary */}
          <div style={{
            background: 'var(--bg-raised)', borderRadius: 'var(--radius-md)',
            padding: 'var(--space-3) var(--space-4)',
            border: '1px solid var(--border-subtle)',
            display: 'flex', alignItems: 'center', gap: 'var(--space-4)',
          }}>
            <span style={{ fontSize: 20 }}>📷</span>
            <div>
              <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-sm)' }}>
                <strong style={{ color: 'var(--text-primary)' }}>{photos.length}</strong> photo{photos.length !== 1 ? 's' : ''} added
                {' · '}
                <strong style={{ color: photos.filter(p => p.orientation).length === photos.length ? 'var(--green-qi)' : 'var(--gold-bright)' }}>
                  {photos.filter(p => p.orientation).length}/{photos.length}
                </strong> with orientation
              </p>
              <p style={{ color: 'var(--text-muted)', fontSize: 'var(--text-xs)', marginTop: 2 }}>
                {photos.filter(p => p.orientation).length < photos.length
                  ? 'Set a facing direction for each photo for more accurate analysis'
                  : 'All photos have orientation — AI will use directional context for all views'}
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

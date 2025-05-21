import React, { useState } from 'react';

interface LinksToggleProps {
  onChange?: (mode: 'hide' | 'hover' | 'show') => void;
  initialMode?: 'hide' | 'hover' | 'show';
}

const options: Array<'hide' | 'hover' | 'show'> = ['hide', 'hover', 'show'];

export function handleToggleChange(option: 'hide' | 'hover' | 'show') {
  const desc = document.getElementById('description');
  if (desc) {
    // Remove any previous links-* classes
    desc.classList.remove('links-hide', 'links-hover', 'links-show');
    switch (option) {
      case 'hide':
        desc.classList.add('links-hide');
        break;
      case 'hover':
        desc.classList.add('links-hover');
        break;
      case 'show':
        desc.classList.add('links-show');
        break;
      default:
        break;
    }
  }
};

export const LinksToggle: React.FC<LinksToggleProps> = ({ onChange, initialMode = 'show' }) => {
  const [selected, setSelected] = useState<'hide' | 'hover' | 'show'>(initialMode);
  const [linksMode, setLinksMode] = useState<'hide' | 'hover' | 'show'>('show');

  const handleClick = () => {
    const currentIndex = options.indexOf(selected);
    const nextIndex = (currentIndex + 1) % options.length;
    const nextOption = options[nextIndex];
    setSelected(nextOption);
    handleToggleChange(nextOption);
    if (onChange) {
      onChange(nextOption);
    }
  };

  const selectedIndex = options.indexOf(selected);

  return (
    <div id="links-toggle-container" style={{
          width: 'fit-content',
          alignItems: 'center',
          display: 'flex',
          flexDirection: 'column',
          padding: '2px 2px',
        }}
      >
      <label>
        Links
      </label>
      <div id="links-toggle"
        style={{
          position: 'relative',
          width: 48,
          background: 'rgb(34, 34, 34)',
          color: 'rgb(250, 250, 250)',
          border: '3px solid rgb(70, 70, 70)',
          borderRadius: '24px',
          height: 24,
          cursor: 'pointer',
          userSelect: 'none',
          boxShadow: '0 1px 4px rgba(0,0,0,0.08)'
        }}
        onClick={handleClick}
        tabIndex={0}
        role="button"
        aria-label={`Toggle links mode (current: ${selected})`}
        onKeyDown={e => {
          if (e.key === 'Enter' || e.key === ' ') handleClick();
        }}
      >
      <div
        id="links-toggle-slider"
        style={{
          position: 'absolute',
          top: 0,
          left:  selectedIndex * 12 + 'px',
          width: '18px',
          height: '18px',
          background: 'rgb(100, 100, 100)',
          borderRadius: '16px',
          transition: 'left 0.2s',
          zIndex: 1,
        }}
      />
    </div>
      <label>
      {selected.charAt(0).toUpperCase() + selected.slice(1)}
      </label>
    </div>
  );
};

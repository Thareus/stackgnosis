import React, { useState } from 'react';

interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    children: React.ReactNode;
}

const Modal = ({ isOpen, onClose, children }: ModalProps) => {
  if (!isOpen) return null;

  return (
    <div className="modal-backdrop">
      <div className="modal">
        <div className="modal-content">
          {children}
        </div>
        <button onClick={onClose} className="modal-close">X</button>
      </div>
    </div>
  );
};

export default Modal;
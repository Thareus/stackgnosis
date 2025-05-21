import React, { useEffect, useState } from 'react';
import Modal from './Modal';
import RequestNewEntryForm from '../forms/RequestNewEntryForm';

interface ModalManagerProps {
  isOpen: boolean;
  onClose: () => void;
  contentType: string;
}

const ModalManager = ({ isOpen, onClose, contentType }: ModalManagerProps) => {
  const [modalContent, setModalContent] = useState<React.ReactNode>(null);

  useEffect(() => {
    switch (contentType) {
      case 'requestNewEntryForm':
        setModalContent(<RequestNewEntryForm />);
        break;
      default:
        setModalContent(null);
    }
  }, [contentType]);

  return (
    <>
      <Modal isOpen={isOpen} onClose={onClose}>
        {modalContent}
      </Modal>
    </>
  );
};

export default ModalManager;
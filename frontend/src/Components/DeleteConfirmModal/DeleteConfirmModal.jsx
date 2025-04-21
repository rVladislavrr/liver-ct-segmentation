import React from 'react';
import Modal from 'react-modal';
import './DeleteConfirmModal.css';

const DeleteConfirmationModal = ({ isOpen, onClose, onConfirm }) => (
  <Modal
    isOpen={isOpen}
    onRequestClose={onClose}
    className="confirmation-modal"
    overlayClassName="confirmation-modal-overlay"
  >
    <div className="confirmation-content">
      <h3>Удалить фото?</h3>
      <div className="confirmation-buttons">
        <button
          className="confirm-btn"
          onClick={() => {
            onConfirm();
            onClose();
          }}
        >
          Удалить
        </button>
        <button
          className="cancel-btn"
          onClick={onClose}
        >
          Отмена
        </button>
      </div>
    </div>
  </Modal>
);

export default DeleteConfirmationModal;

import React, { useState, useEffect } from 'react';
import { deletePhoto, fetchUserProfile } from '../../api/profileApi';
import Modal from 'react-modal';
import './Profile.css';
import { Link } from 'react-router-dom';
import avatar from './avatar.svg';
import DeleteConfirmationModal from '../DeleteConfirmModal/DeleteConfirmModal';

const Profile = () => {
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [photosByFile, setPhotosByFile] = useState({});
  const [photos, setPhotos] = useState(photosByFile);
  const [deleteConfirmModal, setDeleteConfirmModal] = useState({
    isOpen: false,
    photoUuid: null,
    fileUuid: null,
  });

  useEffect(() => {
    const loadProfileData = async () => {
      try {
        const data = await fetchUserProfile();
        setUserData(data);
        const grouped = {};
        data.saved_photos_direct?.forEach((photo) => {
          if (!grouped[photo.file.filename]) {
            grouped[photo.file.filename] = {
              file_info: photo.file,
              photos: [],
            };
          }
          grouped[photo.file.filename].photos.push(photo);
        });
        setPhotosByFile(grouped);
      } catch (err) {
        console.error('Profile load error', err);
        setError(err.response?.data?.message || 'Ошибка загрузки профиля');
      } finally {
        setLoading(false);
      }
    };
    loadProfileData();
  }, []);

  const openModal = (file) => {
    setSelectedFile(file);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  const handleDeletePhoto = async (fileUuid, photoUuid) => {
    try {
      await deletePhoto(photoUuid);

      setPhotos((prev) => {
        const updated = { ...prev };
        updated[fileUuid].photos = updated[fileUuid].photos.filter((p) => p.uuid !== photoUuid);

        if (updated[fileUuid].photos.length === 0) {
          delete updated[fileUuid];
        }

        return updated;
      });

      if (selectedFile?.photos.some((p) => p.uuid === photoUuid)) {
        setSelectedFile((prev) => ({
          ...prev,
          photos: prev.photos.filter((p) => p.uuid !== photoUuid),
        }));
      }
    } catch (error) {
    }
  };

  if (loading) {
    return <div className="profile-loading">Загрузка данных профиля...</div>;
  }
  if (error) {
    return <div className="profile-error">{error}</div>;
  }

  return (
    <>
      <div className="profile-header">
        <p className="title-website">Веб-сервис для сегментации снимков КТ печени</p>
        <div className="back-btn">
          <Link to="/">
            <button className="header-back-button">На главную</button>
          </Link>
        </div>
      </div>
      <div className="profile-container">
        <p className="profile-title">Личный кабинет</p>
        <div className="profile-info">
          <div className="avatar-wrapper">
            <img
              src={avatar}
              alt="avatar-icon"
              className="profile-avatar"
              width={'80px'}
            />
          </div>
          <div className="profile-info-text">
            <p className="profile-name">{userData?.name}</p>
            <p className="profile-email">{userData?.email}</p>
          </div>
        </div>

        <div className="saved-photos">
          <p className="saved-photos-title">Сохранённые фотографии</p>
          {Object.keys(photosByFile).length > 0 ? (
            <ul className="file-list">
              {Object.entries(photosByFile).map(([fileUuid, { file_info, photos }]) => (
                <li
                  key={fileUuid}
                  className="file-item"
                >
                  <button
                    className="file-link"
                    onClick={() => {
                      setSelectedFile({ fileInfo: file_info, photos });
                      setIsModalOpen(true);
                    }}
                  >
                    {file_info.filename} ({photos.length} фото)
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <p className="no-saved-photos-msg">Нет сохраненных фотографий</p>
          )}
        </div>

        <Modal
          isOpen={isModalOpen}
          onRequestClose={closeModal}
          className="photo-modal"
          overlayClassName="photo-modal-overlay"
        >
          <button
            className="close-modal"
            onClick={closeModal}
          >
            ×
          </button>
          <p className="modal-title-file">{selectedFile?.fileInfo.filename}</p>
          <div className="photos-grid">
            {selectedFile?.photos.map((photo) => (
              <div
                key={photo.uuid}
                className="photo-item"
              >
                <img
                  src={photo.url}
                  alt={photo.name}
                  className="photo-image"
                />
                <p className="modal-title-photo">{photo.name}</p>
                <div className="photo-meta-wrapper">
                  <div className="photo-meta">
                    <span className="save-date-label">Сохранено</span>
                    <span className="save-date-value">
                      {new Date(photo.create_at + 'Z').toLocaleDateString('ru-RU', {
                        day: 'numeric',
                        month: 'long',
                        year: 'numeric',
                      })}
                      <br />
                      {new Date(photo.create_at + 'Z').toLocaleTimeString('ru-RU', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                  <button
                    className="delete-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      setDeleteConfirmModal({
                        isOpen: true,
                        photoUuid: photo.uuid,
                        fileUuid: selectedFile.fileInfo.uuid,
                      });
                    }}
                  >
                    <svg
                      className="delete-icon"
                      viewBox="0 0 24 24"
                    >
                      <path
                        fill="currentColor"
                        d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"
                      />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </Modal>
        <DeleteConfirmationModal
          isOpen={deleteConfirmModal.isOpen}
          onClose={() => setDeleteConfirmModal({ isOpen: false, photoUuid: null, fileUuid: null })}
          onConfirm={() => handleDeletePhoto(deleteConfirmModal.fileUuid, deleteConfirmModal.photoUuid)}
        />
      </div>
    </>
  );
};

export default Profile;

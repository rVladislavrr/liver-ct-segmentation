import React, { useState, useEffect } from 'react';
import { fetchUserProfile } from '../../api/profileApi';
import Modal from 'react-modal';

const Profile = () => {
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [photosByFile, setPhotosByFile] = useState({});

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

  if (loading) {
    return <div className="profile-loading">Загрузка данных профиля...</div>;
  }
  if (error) {
    return <div className="profile-error">{error}</div>;
  }

  return (
    <div className="profile-container">
      <p>Личный кабинет</p>
      <div className="profile-info">
        <p>Имя: {userData?.name}</p>
        <p>Email: {userData?.email}</p>
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
        <p>{selectedFile?.fileInfo.filename}</p>
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
              <p>{photo.name}</p>
              <p>Сохранено: {new Date(photo.create_at).toLocaleString()}</p>
            </div>
          ))}
        </div>
      </Modal>
    </div>
  );
};

export default Profile;

import React, { useState, useEffect } from 'react';
import { fetchUserProfile } from '../../api/profileApi';

const Profile = () => {
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  useEffect(() => {
    const loadProfileData = async () => {
      try {
        const data = await fetchUserProfile();
        setUserData(data);
      } catch (err) {
        console.error('Profile load error', err);
        setError(err.response?.data?.message || 'Ошибка загрузки профиля');
      } finally {
        setLoading(false);
      }
    };
    loadProfileData();
  }, []);

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
    </div>
  );
};

export default Profile;

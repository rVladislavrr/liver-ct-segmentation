import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Header.css';
import { logout } from '../../api/commonApi';
const Header = () => {
  const [isAuth, setIsAuth] = useState(!!localStorage.getItem('accessToken'));
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      setIsAuth(false);
      navigate('/');
    } catch (error) {
      console.error('Logout error', error);
    }
  };

  return (
    <div className="main-header">
      <p className="header-title">Веб-сервис для сегментации снимков КТ печени</p>
      <div className="registration-header">
        {isAuth ? (
          <>
            <Link to="/profile">
              <button className="header-profile-button">Личный кабинет</button>
            </Link>
            <button
              className="header-logout-button"
              onClick={handleLogout}
            >
              Выйти
            </button>
          </>
        ) : (
          <>
            <Link to="/login">
              <button className="header-login-button">Войти</button>
            </Link>
            <Link to="/registration">
              <button className="header-registration-button">Регистрация</button>
            </Link>
          </>
        )}
      </div>
    </div>
  );
};

export default Header;

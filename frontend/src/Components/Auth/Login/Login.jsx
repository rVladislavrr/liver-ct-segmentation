import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { login } from '../../../api/commonApi.js';
import './Login.css';
import { validateEmail, validatePassword } from '../../../utils/validationAuth.js';

const Login = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [formError, setFormError] = useState('');
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const [errors, setErrors] = useState({
    email: '',
    password: '',
  });

  const validateForm = () => {
    let isValid = true;
    const newErrors = {
      email: '',
      password: '',
    };

    // Валидация email
    if (!formData.email) {
      newErrors.email = 'Email обязателен';
      isValid = false;
    } else if (!validateEmail(formData.email)) {
      newErrors.email = 'Введите корректный email';
      isValid = false;
    }

    // Валидация пароля
    if (!formData.password) {
      newErrors.password = 'Пароль обязателен';
      isValid = false;
    } else if (!validatePassword(formData.password)) {
      newErrors.password = 'Пароль должен содержать минимум 6 символов';
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    try {
      const result = await login(formData.email, formData.password);
  
      if (result.success) {
        navigate('/');
      } else {
        setFormError(result.error || 'Неверный email или пароль');
      }
    } catch (error) {
      setFormError(error.message || 'Произошла ошибка при входе');
      console.error('Login error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const isFormValid = formData.email && formData.password && 
                     validateEmail(formData.email) && 
                     validatePassword(formData.password);

  return (
    <>
      <div className="auth-header">
        <p className="title-website">Веб-сервис для сегментации снимков КТ печени</p>
      </div>
      <div className="login-container">
        <p className="title-login">Вход</p>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email:</label>
            <input
              type="email"
              id="email"
              name="email"
              placeholder="Введите email"
              value={formData.email}
              onChange={handleChange}
              className={errors.email ? 'error-input' : ''}
            />
            {errors.email && <div className="error-text">{errors.email}</div>}
          </div>

          <div className="form-group">
            <label htmlFor="password">Пароль:</label>
            <input
              type="password"
              id="password"
              name="password"
              placeholder="Введите пароль"
              value={formData.password}
              onChange={handleChange}
              className={errors.password ? 'error-input' : ''}
            />
            {errors.password && <div className="error-text">{errors.password}</div>}
          </div>

          <button
            type="submit"
            disabled={isLoading || !isFormValid}
            className={`submit-button ${isLoading ? 'loading' : ''}`}
          >
            {isLoading ? 'Загрузка...' : 'Войти'}
          </button>
          <div className="register-link">
            Нет аккаунта?
            <Link to={'/registration'}> Регистрация</Link>
          </div>
        </form>
        
      </div>
    </>
  );
};

export default Login;
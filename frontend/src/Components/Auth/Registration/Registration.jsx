import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { register } from '../../../api/commonApi.js';
import { validateRegistrationForm, validateEmail, validatePassword } from '../../../utils/validationAuth.js';

const Registration = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [formError, setFormError] = useState('');
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
  });

  const [errors, setErrors] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');

    const { isValid, errors: validationErrors } = validateRegistrationForm(formData);
    if (!isValid) {
      setErrors(validationErrors);
      return;
    }

    setIsLoading(true);
    try {
      const result = await register(formData.name, formData.email, formData.password);

      if (result.success) {
        navigate('/login');
      } else {
        setFormError(result.error);
      }
      setIsLoading(false);
    } catch (error) {
      setFormError(error.message || 'Произошла ошибка при входе');
      console.error('Login error:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    setErrors((prev) => ({
      ...prev,
      [name]: '',
    }));
  };

  const isFormValid = validateEmail(formData.email) && validatePassword(formData.password) && formData.password === formData.confirmPassword && formData.name.trim() !== '';

  return (
    <>
      <div className="auth-header">
        <p className="title-website">Веб-сервис для сегментации снимков КТ печени</p>
      </div>
      <div className="login-container">
        <p className="title-login">Регистрация</p>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Имя:</label>
            <input
              type="text"
              id="name"
              name="name"
              placeholder="Введите ваше имя"
              value={formData.name}
              onChange={handleChange}
              className={errors.name ? 'error-input' : ''}
              required
            />
            {errors.name && <div style={{ color: 'red', fontSize: '0.8rem' }}>{errors.name}</div>}
          </div>

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
              required
            />
            {errors.email && <div style={{ color: 'red', fontSize: '0.8rem' }}>{errors.email}</div>}
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
              required
            />
            {errors.password && <div style={{ color: 'red', fontSize: '0.8rem' }}>{errors.password}</div>}
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Подтвердите пароль:</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              placeholder="Повторите пароль"
              value={formData.confirmPassword}
              onChange={handleChange}
              className={errors.confirmPassword ? 'error-input' : ''}
              required
            />
            {errors.confirmPassword && <div style={{ color: 'red', fontSize: '0.8rem' }}>{errors.confirmPassword}</div>}
          </div>

          <button
            type="submit"
            disabled={isLoading || !isFormValid}
            className="submit-button"
          >
            Зарегистрироваться
          </button>
          <div className="register-link">
            Уже есть аккаунт?
            <Link to={'/login'}> Войти</Link>
          </div>
        </form>
      </div>
    </>
  );
};

export default Registration;

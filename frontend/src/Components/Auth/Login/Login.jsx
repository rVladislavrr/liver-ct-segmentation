import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { login } from '../../../api/commonApi.js';
import './Login.css';
import { validateLoginForm, validateEmail, validatePassword } from '../../../utils/validationAuth.js'

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');
    const { isValid, errors: validationErrors } = validateLoginForm(formData);
    if (!isValid) {
      setErrors(validationErrors);
      return;
    }

    setIsLoading(true);
    const result = await login(formData.email, formData.password);

    if (result.success) {
      navigate('/');
    } else {
      setFormError(result.error);
    }
    setIsLoading(false);
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

  const isFormValid = validateEmail(formData.email) && validatePassword(formData.password);

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

          <button
            type="submit"
            disabled={isLoading || !isFormValid}
            className="submit-button"
          >
            Войти
          </button>
          <div className="register-link">
            Нет аккаунта?
            <Link to={'/registration'}> Регистрация</Link>
          </div>
        </form>
        {formError && <div className="error-message">{formError}</div>}
      </div>
    </>
  );
};

export default Login;

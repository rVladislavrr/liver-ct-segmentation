export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(String(email).toLowerCase());
};

export const validatePassword = (password) => {
  return password.length >= 8;
};

export const validateName = (name) => {
  return name.trim().length > 2;
};

export const validateLoginForm = (formData) => {
  const errors = { email: '', password: '' };
  let isValid = true;

  if (!formData.email) {
    errors.email = 'Email обязателен';
    isValid = false;
  } else if (!validateEmail(formData.email)) {
    errors.email = 'Введите корректный email';
    isValid = false;
  }

  if (!formData.password) {
    errors.password = 'Пароль обязателен';
    isValid = false;
  } else if (!validatePassword(formData.password)) {
    errors.password = 'Пароль должен содержать минимум 8 символов';
    isValid = false;
  }

  return { isValid, errors };
};

export const validateRegistrationForm = (formData) => {
  const errors = { email: '', password: '', confirmPassword: '', name: '' };
  let isValid = true;

  if (!formData.name) {
    errors.name = 'Имя обязательно';
    isValid = false;
  } else if (!validateName(formData.name)) {
    errors.name = 'Длина имени должна быть больше 2 символов';
    isValid = false;
  }

  if (!formData.email) {
    errors.email = 'Email обязателен';
    isValid = false;
  } else if (!validateEmail(formData.email)) {
    errors.email = 'Введите корректный email';
    isValid = false;
  }

  if (!formData.password) {
    errors.password = 'Пароль обязателен';
    isValid = false;
  } else if (!validatePassword(formData.password)) {
    errors.password = 'Пароль должен содержать минимум 8 символов';
    isValid = false;
  }

  if (formData.password !== formData.confirmPassword) {
    errors.confirmPassword = 'Пароли не совпадают';
    isValid = false;
  }

  return { isValid, errors };
};

export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

export const validatePassword = (password) => {
  if (!password) return { valid: false, message: 'Password is required' };
  if (password.length < 8) return { valid: false, message: 'Password must be at least 8 characters' };
  return { valid: true, message: '' };
};

export const validateImage = (file) => {
  if (!file) return { valid: false, message: 'Image is required' };
  
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
  if (!validTypes.includes(file.type)) {
    return { valid: false, message: 'Only JPG, JPEG and PNG files are allowed' };
  }
  
  const maxSize = 10 * 1024 * 1024; // 10MB
  if (file.size > maxSize) {
    return { valid: false, message: 'Image size must be less than 10MB' };
  }
  
  return { valid: true, message: '' };
};

export const validateComplaint = (data) => {
  const errors = {};
  
  if (!data.category) errors.category = 'Category is required';
  if (!data.description || data.description.length < 10) errors.description = 'Description must be at least 10 characters';
  if (!data.location || !data.location.lat || !data.location.lng) errors.location = 'Location is required';
  
  return {
    valid: Object.keys(errors).length === 0,
    errors
  };
};

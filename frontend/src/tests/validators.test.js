import { describe, it, expect } from 'vitest';
import {
  validateEmail,
  validatePassword,
  validateImage,
  validateComplaint,
} from '../utils/validators';

describe('Frontend Validators Unit Tests', () => {
  it('validates email addresses correctly', () => {
    expect(validateEmail('test@example.com')).toBe(true);
    expect(validateEmail('user.name+tag@sub.domain.org')).toBe(true);
    expect(validateEmail('invalid-email')).toBe(false);
    expect(validateEmail('@domain.com')).toBe(false);
    expect(validateEmail('')).toBe(false);
  });

  it('validates password requirements', () => {
    expect(validatePassword('').valid).toBe(false);
    expect(validatePassword('short').valid).toBe(false);
    expect(validatePassword('validPassword123').valid).toBe(true);
  });

  it('validates image uploads properly', () => {
    expect(validateImage(null).valid).toBe(false);

    const validFile = { type: 'image/jpeg', size: 1024 * 1024 };
    expect(validateImage(validFile).valid).toBe(true);

    const pngFile = { type: 'image/png', size: 2 * 1024 * 1024 };
    expect(validateImage(pngFile).valid).toBe(true);

    const invalidType = { type: 'application/pdf', size: 1024 };
    expect(validateImage(invalidType).valid).toBe(false);

    const oversized = { type: 'image/jpeg', size: 15 * 1024 * 1024 };
    expect(validateImage(oversized).valid).toBe(false);
  });

  it('validates complaint submission payload', () => {
    const invalidData = { category: '', description: '', location: null };
    const res1 = validateComplaint(invalidData);
    expect(res1.valid).toBe(false);
    expect(res1.errors.category).toBeTruthy();
    expect(res1.errors.description).toBeTruthy();
    expect(res1.errors.location).toBeTruthy();

    const validData = {
      category: 'pothole',
      description: 'Severe road depression causing vehicle damage',
      location: { lat: 12.9716, lng: 77.5946 },
    };
    const res2 = validateComplaint(validData);
    expect(res2.valid).toBe(true);
    expect(Object.keys(res2.errors).length).toBe(0);
  });
});

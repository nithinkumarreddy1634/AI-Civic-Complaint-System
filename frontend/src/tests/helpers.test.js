import { describe, it, expect } from 'vitest';
import {
  formatDate,
  getImageUrl,
  formatStatus,
  getSeverityColor,
  getPriorityColor,
  getCategoryMeta,
  truncateText,
  formatCoordinates,
} from '../utils/helpers';

describe('Frontend Helpers Unit Tests', () => {
  it('formats dates properly', () => {
    expect(formatDate(null)).toBe('—');
    expect(formatDate('')).toBe('—');
    const valid = formatDate('2026-10-06T12:00:00Z');
    expect(valid).toBeTruthy();
    expect(typeof valid).toBe('string');
  });

  it('formats image URLs correctly', () => {
    expect(getImageUrl(null)).toBeNull();
    expect(getImageUrl('http://example.com/img.jpg')).toBe('http://example.com/img.jpg');
    expect(getImageUrl('https://example.com/img.jpg')).toBe('https://example.com/img.jpg');
    expect(getImageUrl('uploads/test.jpg')).toContain('test.jpg');
  });

  it('formats status and colors accurately', () => {
    expect(formatStatus('SUBMITTED')).toBeTruthy();
    expect(getPriorityColor('URGENT')).toContain('rose');
    expect(getPriorityColor('LOW')).toContain('slate');
    expect(getSeverityColor('CRITICAL')).toBeTruthy();
  });

  it('finds category metadata', () => {
    const meta = getCategoryMeta('pothole');
    expect(meta.label).toBe('Pothole');
    const fallback = getCategoryMeta('unknown_custom');
    expect(fallback.value).toBe('unknown_custom');
  });

  it('truncates text at specified boundary', () => {
    expect(truncateText('Hello world', 5)).toBe('Hello...');
    expect(truncateText('Short', 10)).toBe('Short');
    expect(truncateText('', 5)).toBe('');
  });

  it('formats coordinates to precision', () => {
    expect(formatCoordinates(null, null)).toBe('Not available');
    expect(formatCoordinates(12.971598, 77.594562)).toBe('12.97160°, 77.59456°');
  });
});

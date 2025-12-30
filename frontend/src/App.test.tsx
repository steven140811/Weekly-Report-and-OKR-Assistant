import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders app header', () => {
  render(<App />);
  const headerElement = screen.getByText(/WorkPilot 效能助手/i);
  expect(headerElement).toBeInTheDocument();
});

test('renders weekly report tab', () => {
  render(<App />);
  const tabElements = screen.getAllByText(/周报生成/i);
  expect(tabElements.length).toBeGreaterThan(0);
});

test('renders OKR tab', () => {
  render(<App />);
  const tabElement = screen.getByRole('button', { name: /OKR 生成/i });
  expect(tabElement).toBeInTheDocument();
});

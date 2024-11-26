import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ReaderSettings from '../components/features/reader/ReaderSettings';

describe('ReaderSettings Component', () => {
  const mockTheme = {
    backgroundColor: '#F6F3E9',
    textColor: '#2c2c2c',
  };

  test('les paramètres sont appliqués', () => {
    const mockOnThemeChange = jest.fn();
    const mockOnSpeedChange = jest.fn();

    render(
      <ReaderSettings
        open={true}
        onClose={() => {}}
        theme={mockTheme}
        speed={5}
        onSpeedChange={mockOnSpeedChange}
        onThemeChange={mockOnThemeChange}
      />
    );

    // Test du changement de taille de police
    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: 20 } });
    expect(mockOnThemeChange).toHaveBeenCalledWith('fontSize', '20px');
  });

  test('le changement de thème fonctionne', () => {
    const mockOnThemeChange = jest.fn();

    render(
      <ReaderSettings
        open={true}
        onClose={() => {}}
        theme={mockTheme}
        speed={5}
        onThemeChange={mockOnThemeChange}
      />
    );

    // Test du changement de thème
    const themeButton = screen.getByText('Nuit');
    fireEvent.click(themeButton);
    expect(mockOnThemeChange).toHaveBeenCalledWith('theme', expect.objectContaining({
      backgroundColor: '#131516',
      textColor: '#e1e1e1',
    }));
  });
});

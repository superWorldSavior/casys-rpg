import React from 'react';
import { render, fireEvent, screen, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import KindleReader from '../components/features/reader/KindleReader';

describe('KindleReader Component', () => {
  const mockContent = ['Chapitre 1', 'Chapitre 2'];
  const mockBookId = 'test-book';
  const mockTheme = {
    backgroundColor: '#F6F3E9',
    textColor: '#2c2c2c',
  };

  test('affiche correctement le contenu initial', () => {
    render(
      <KindleReader
        content={mockContent}
        initialSection={0}
        bookId={mockBookId}
        customTheme={mockTheme}
      />
    );

    expect(screen.getByText('Chapitre 1')).toBeInTheDocument();
  });

  test('navigation entre les chapitres fonctionne', () => {
    const { container } = render(
      <KindleReader
        content={mockContent}
        initialSection={0}
        bookId={mockBookId}
        customTheme={mockTheme}
      />
    );

    // Simuler la navigation avec les touches
    fireEvent.keyDown(container, { key: 'ArrowRight' });
    expect(screen.getByText('Chapitre 2')).toBeInTheDocument();

    fireEvent.keyDown(container, { key: 'ArrowLeft' });
    expect(screen.getByText('Chapitre 1')).toBeInTheDocument();
  });

  test('le thème est correctement appliqué', () => {
    const customTheme = {
      backgroundColor: '#000000',
      textColor: '#ffffff',
    };

    const { container } = render(
      <KindleReader
        content={mockContent}
        initialSection={0}
        bookId={mockBookId}
        customTheme={customTheme}
      />
    );

    const readerContainer = container.querySelector('.kindle-reader-content');
    expect(readerContainer).toHaveStyle({
      backgroundColor: '#000000',
      color: '#ffffff',
    });
  });

  test('la progression est sauvegardée', () => {
    const mockOnProgressChange = jest.fn();

    render(
      <KindleReader
        content={mockContent}
        initialSection={0}
        bookId={mockBookId}
        customTheme={mockTheme}
        onProgressChange={mockOnProgressChange}
      />
    );

    expect(localStorage.setItem).toHaveBeenCalledWith(
      expect.stringContaining(mockBookId),
      expect.any(String)
    );
  });
});

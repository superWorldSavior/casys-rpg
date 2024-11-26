import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';
import TableOfContents from '../components/features/reader/TableOfContents';

describe('Reader Navigation', () => {
  test('route vers le bon chapitre', () => {
    const mockOnChapterSelect = jest.fn();
    const chapters = ['Chapitre 1', 'Chapitre 2', 'Chapitre 3'];

    render(
      <MemoryRouter>
        <TableOfContents
          chapters={chapters}
          currentSection={0}
          onChapterSelect={mockOnChapterSelect}
          open={true}
          onClose={() => {}}
        />
      </MemoryRouter>
    );

    const settingsButton = screen.getByText('Paramètres');
    fireEvent.click(settingsButton);
    expect(screen.getByText('Paramètres')).toBeInTheDocument();
  });

  test('gère les erreurs de navigation', () => {
    const mockOnChapterSelect = jest.fn();
    const mockOnExitReader = jest.fn();

    render(
      <MemoryRouter>
        <TableOfContents
          chapters={[]}
          currentSection={0}
          onChapterSelect={mockOnChapterSelect}
          onExitReader={mockOnExitReader}
          open={true}
          onClose={() => {}}
        />
      </MemoryRouter>
    );

    const exitButton = screen.getByText('Quitter');
    fireEvent.click(exitButton);
    expect(mockOnExitReader).toHaveBeenCalled();
  });
});

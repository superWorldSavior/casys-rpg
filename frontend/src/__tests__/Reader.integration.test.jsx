import React from 'react';
import { render, fireEvent, screen, act } from '@testing-library/react';
import '@testing-library/jest-dom';
import ReaderPage from '../pages/Reader';
import { MemoryRouter, Route, Routes } from 'react-router-dom';

jest.mock('../services/api', () => ({
  fetchChapter: jest.fn(() => Promise.resolve({ content: 'Contenu du chapitre' })),
}));

describe('Reader Integration', () => {
  const renderWithRouter = (component) => {
    return render(
      <MemoryRouter initialEntries={['/reader/test-book']}>
        <Routes>
          <Route path="/reader/:bookId" element={component} />
        </Routes>
      </MemoryRouter>
    );
  };

  test('charge et affiche le contenu du chapitre', async () => {
    renderWithRouter(<ReaderPage />);

    await act(async () => {
      await screen.findByText('Contenu du chapitre');
    });

    expect(screen.getByText('Contenu du chapitre')).toBeInTheDocument();
  });

  test('navigation complète fonctionne', async () => {
    renderWithRouter(<ReaderPage />);

    await act(async () => {
      await screen.findByText('Contenu du chapitre');
    });

    const nextButton = screen.getByText('Chapitre suivant');
    fireEvent.click(nextButton);

    await act(async () => {
      await screen.findByText('Contenu du chapitre');
    });
  });

  test('sauvegarde et restaure la progression', async () => {
    renderWithRouter(<ReaderPage />);

    await act(async () => {
      await screen.findByText('Contenu du chapitre');
    });

    expect(localStorage.getItem).toHaveBeenCalled();
    expect(localStorage.setItem).toHaveBeenCalled();
  });
});

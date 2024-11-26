import { renderHook, act } from '@testing-library/react-hooks';
import useReader from '../hooks/useReader';

describe('useReader Hook', () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
  });

  test('gère correctement l'état de lecture', () => {
    const { result } = renderHook(() => useReader('test-book'));

    act(() => {
      result.current.setProgress(50);
    });

    expect(result.current.progress).toBe(50);
    expect(localStorage.setItem).toHaveBeenCalledWith(
      expect.stringContaining('test-book'),
      expect.any(String)
    );
  });

  test('sauvegarde la progression', () => {
    const { result } = renderHook(() => useReader('test-book'));

    act(() => {
      result.current.setCurrentChapter(2);
      result.current.setProgress(75);
    });

    expect(localStorage.setItem).toHaveBeenCalledWith(
      expect.stringContaining('test-book'),
      expect.stringContaining('75')
    );
  });
});

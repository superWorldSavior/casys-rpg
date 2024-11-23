import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import TextDisplay from '../../components/features/reader/TextDisplay';
import NavigationControls from '../../components/features/reader/NavigationControls';
import CommandInput from '../../components/features/reader/CommandInput';
import SpeedControl from '../../components/features/reader/SpeedControl';
import ThemeControl from '../../components/features/reader/ThemeControl';
import { storageService } from '../../services/storage';

const DEFAULT_THEME = {
  fontFamily: 'var(--bs-body-font-family)',
  fontSize: '1rem',
  textColor: '#ffffff',
  lineHeight: '1.6'
};

function ReaderPage() {
  const { bookId } = useParams();
  const [currentSection, setCurrentSection] = useState(-1);
  const [isPaused, setIsPaused] = useState(true);
  const [speed, setSpeed] = useState(5);
  const [textContent, setTextContent] = useState([]);
  const [theme, setTheme] = useState(DEFAULT_THEME);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchContent = async () => {
      try {
        const chapters = await storageService.getAllChapters();
        if (chapters && chapters.length > 0) {
          const content = await Promise.all(
            chapters.map(key => storageService.getChapter(key))
          );
          setTextContent(content);
        } else {
          const response = await fetch(`/api/books/${bookId}/content`);
          const data = await response.json();
          if (response.ok) {
            await Promise.all(
              data.map((content, index) => 
                storageService.saveChapter(`book_${bookId}_chapter_${index + 1}`, content)
              )
            );
            setTextContent(data);
          } else {
            setError('Error loading book content');
          }
        }

        const savedTheme = await storageService.getChapter('user_theme');
        if (savedTheme) {
          setTheme(savedTheme);
        }
      } catch (error) {
        console.error('Error fetching content:', error);
        setError('Error loading book content');
      }
    };

    if (bookId) {
      fetchContent();
    }
  }, [bookId]);

  useEffect(() => {
    storageService.saveChapter('user_theme', theme);
  }, [theme]);

  if (error) {
    return (
      <div className="alert alert-danger" role="alert">
        {error}
      </div>
    );
  }

  return (
    <div className="row justify-content-center">
      <div className="col-md-8">
        <div className="card">
          <div className="card-body">
            <TextDisplay
              textContent={textContent}
              currentSection={currentSection}
              speed={speed}
              theme={theme}
            />
            <NavigationControls
              currentSection={currentSection}
              setCurrentSection={setCurrentSection}
              totalSections={textContent.length}
              isPaused={isPaused}
              setIsPaused={setIsPaused}
            />
            <SpeedControl speed={speed} setSpeed={setSpeed} />
            <ThemeControl theme={theme} onThemeChange={setTheme} />
            <CommandInput
              onCommand={(command) => {
                switch (command) {
                  case 'commencer':
                    setCurrentSection(0);
                    setIsPaused(false);
                    break;
                  case 'pause':
                    setIsPaused(true);
                    break;
                  case 'resume':
                    setIsPaused(false);
                    break;
                  case 'skip':
                    if (currentSection < textContent.length - 1) {
                      setCurrentSection(prev => prev + 1);
                    }
                    break;
                  case 'help':
                    alert(`Available commands:
- commencer: Start reading
- pause: Pause reading
- resume: Resume reading
- skip: Skip to next section
- help: Show this help message`);
                    break;
                }
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default ReaderPage;

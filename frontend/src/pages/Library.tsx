import { AudioPlayer } from '@/components/AudioPlayer';
import { BottomNav } from '@/components/BottomNav';

export const Library = () => {
  const books = [
    {
      id: '1',
      title: 'Sample Audiobook',
      progress: 45,
      url: 'https://example.com/sample-audio.mp3',
    },
    // Add more sample books here
  ];

  return (
    <div className="min-h-screen bg-background pb-32">
      <header className="border-b p-4">
        <h1 className="text-2xl font-bold">Your Library</h1>
      </header>

      <main className="p-4">
        <div className="grid gap-4">
          {books.map((book) => (
            <div key={book.id} className="border rounded-lg p-4">
              <h3 className="font-medium">{book.title}</h3>
              <div className="text-sm text-muted-foreground mt-2">
                Progress: {book.progress}%
              </div>
            </div>
          ))}
        </div>
      </main>

      <BottomNav />
      <AudioPlayer
        url={books[0].url}
        title={books[0].title}
        onProgress={() => {}}
      />
    </div>
  );
};

import React, { useState, useRef, useEffect } from 'react';
import { Slider } from './ui/slider';
import { Button } from './ui/button';
import { Play, Pause, SkipBack, SkipForward } from 'lucide-react';

interface AudioPlayerProps {
  url: string;
  title: string;
  onProgress?: (progress: number) => void;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({
  url,
  title,
  onProgress
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const audioRef = useRef<HTMLAudioElement>(null);

  const togglePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      const currentProgress = (audioRef.current.currentTime / audioRef.current.duration) * 100;
      setProgress(currentProgress);
      onProgress?.(currentProgress);
    }
  };

  const handleSliderChange = (value: number[]) => {
    if (audioRef.current) {
      const newTime = (value[0] / 100) * audioRef.current.duration;
      audioRef.current.currentTime = newTime;
      setProgress(value[0]);
    }
  };

  const skip = (seconds: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime += seconds;
    }
  };

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.addEventListener('loadedmetadata', () => {
        setDuration(audioRef.current?.duration || 0);
      });
    }
  }, [url]);

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-background border-t p-4">
      <div className="container max-w-4xl mx-auto">
        <div className="flex flex-col gap-2">
          <div className="text-lg font-medium">{title}</div>
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => skip(-10)}
            >
              <SkipBack className="h-6 w-6" />
            </Button>
            <Button
              variant="default"
              size="icon"
              onClick={togglePlayPause}
            >
              {isPlaying ? (
                <Pause className="h-6 w-6" />
              ) : (
                <Play className="h-6 w-6" />
              )}
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => skip(10)}
            >
              <SkipForward className="h-6 w-6" />
            </Button>
            <div className="flex-1">
              <Slider
                value={[progress]}
                onValueChange={handleSliderChange}
                max={100}
                step={0.1}
              />
            </div>
          </div>
          <audio
            ref={audioRef}
            src={url}
            onTimeUpdate={handleTimeUpdate}
            onEnded={() => setIsPlaying(false)}
          />
        </div>
      </div>
    </div>
  );
};

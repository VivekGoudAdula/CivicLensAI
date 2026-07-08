import { useCallback, useEffect, useRef, useState } from "react";
import { Mic, Pause, Play, Square, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

const MAX_DURATION_SECONDS = 120;
const MAX_BASE64_LENGTH = 700_000;

export interface VoiceRecordingValue {
  data: string;
  mime_type: string;
  duration_seconds: number;
  playbackUrl: string;
}

export interface VoiceRecorderProps {
  value?: VoiceRecordingValue | null;
  onChange: (value: VoiceRecordingValue | null) => void;
  error?: string;
  className?: string;
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
}

async function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      resolve(result.includes(",") ? result.split(",")[1] : result);
    };
    reader.onerror = () => reject(new Error("Failed to read audio"));
    reader.readAsDataURL(blob);
  });
}

export function VoiceRecorder({
  value,
  onChange,
  error,
  className,
}: VoiceRecorderProps) {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<number | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const elapsedRef = useRef(0);

  const [recording, setRecording] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const [levels, setLevels] = useState<number[]>(Array.from({ length: 24 }, () => 0.2));

  const stopTimer = useCallback(() => {
    if (timerRef.current !== null) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  useEffect(() => () => stopTimer(), [stopTimer]);

  const startRecording = useCallback(async () => {
    setLocalError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : "audio/mp4";
      const recorder = new MediaRecorder(stream, { mimeType });
      chunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop());
        const blob = new Blob(chunksRef.current, { type: mimeType });
        const base64 = await blobToBase64(blob);
        const duration = elapsedRef.current;

        if (base64.length > MAX_BASE64_LENGTH) {
          setLocalError("Recording is too large. Please record a shorter message.");
          return;
        }

        onChange({
          data: base64,
          mime_type: mimeType,
          duration_seconds: duration,
          playbackUrl: URL.createObjectURL(blob),
        });
      };

      mediaRecorderRef.current = recorder;
      recorder.start(250);
      setRecording(true);
      setElapsed(0);
      elapsedRef.current = 0;

      timerRef.current = window.setInterval(() => {
        setElapsed((prev) => {
          const next = prev + 1;
          elapsedRef.current = next;
          if (next >= MAX_DURATION_SECONDS) {
            mediaRecorderRef.current?.stop();
            setRecording(false);
            stopTimer();
          }
          return next;
        });
        setLevels(
          Array.from({ length: 24 }, () => 0.15 + Math.random() * 0.85),
        );
      }, 1000);
    } catch {
      setLocalError("Microphone access denied or unavailable.");
    }
  }, [onChange, stopTimer]);

  const stopRecording = useCallback(() => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
    stopTimer();
  }, [stopTimer]);

  const togglePlayback = useCallback(() => {
    if (!value?.playbackUrl) {
      return;
    }
    if (!audioRef.current) {
      audioRef.current = new Audio(value.playbackUrl);
      audioRef.current.onended = () => setPlaying(false);
    }
    if (playing) {
      audioRef.current.pause();
      setPlaying(false);
    } else {
      void audioRef.current.play();
      setPlaying(true);
    }
  }, [playing, value?.playbackUrl]);

  const displayError = error ?? localError;

  return (
    <div className={cn("space-y-4 rounded-xl border p-4", className)}>
      <div className="flex items-center justify-between">
        <div>
          <p className="font-medium">Voice Recording</p>
          <p className="text-sm text-muted-foreground">
            Record a voice note describing your complaint (optional)
          </p>
        </div>
        <span className="font-mono text-sm tabular-nums">
          {formatTime(value?.duration_seconds ?? elapsed)}
        </span>
      </div>

      <div
        className="flex h-12 items-end justify-center gap-1 rounded-lg bg-muted/50 px-3 py-2"
        aria-hidden={!recording}
        role="img"
        aria-label={recording ? "Recording in progress" : "Audio waveform"}
      >
        {levels.map((level, index) => (
          <span
            key={index}
            className={cn(
              "w-1 rounded-full transition-all duration-150",
              recording ? "bg-primary" : "bg-muted-foreground/30",
            )}
            style={{ height: `${level * 100}%` }}
          />
        ))}
      </div>

      {recording ? (
        <Progress value={(elapsed / MAX_DURATION_SECONDS) * 100} className="h-1.5" />
      ) : null}

      <div className="flex flex-wrap gap-2">
        {!value && !recording ? (
          <Button type="button" onClick={() => void startRecording()}>
            <Mic className="h-4 w-4" />
            Start Recording
          </Button>
        ) : null}

        {recording ? (
          <Button type="button" variant="destructive" onClick={stopRecording}>
            <Square className="h-4 w-4" />
            Stop Recording
          </Button>
        ) : null}

        {value && !recording ? (
          <>
            <Button type="button" variant="outline" onClick={togglePlayback}>
              {playing ? (
                <>
                  <Pause className="h-4 w-4" />
                  Pause
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  Play
                </>
              )}
            </Button>
            <Button
              type="button"
              variant="ghost"
              onClick={() => {
                audioRef.current?.pause();
                setPlaying(false);
                onChange(null);
              }}
            >
              <Trash2 className="h-4 w-4" />
              Delete
            </Button>
          </>
        ) : null}
      </div>

      {displayError ? <p className="text-sm text-destructive">{displayError}</p> : null}
    </div>
  );
}

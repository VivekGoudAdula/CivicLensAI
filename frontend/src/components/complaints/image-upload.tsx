import { useCallback, useRef, useState } from "react";
import imageCompression from "browser-image-compression";
import { ImagePlus, Trash2, Upload } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const MAX_FILE_SIZE_MB = 5;
const MAX_BASE64_LENGTH = 700_000;
const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"];

export interface ImageUploadValue {
  data: string;
  mime_type: string;
  file_name: string;
  previewUrl: string;
}

export interface ImageUploadProps {
  value?: ImageUploadValue | null;
  onChange: (value: ImageUploadValue | null) => void;
  error?: string;
  className?: string;
}

async function fileToBase64(file: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      const base64 = result.includes(",") ? result.split(",")[1] : result;
      resolve(base64);
    };
    reader.onerror = () => reject(new Error("Failed to read image file"));
    reader.readAsDataURL(file);
  });
}

export function ImageUpload({
  value,
  onChange,
  error,
  className,
}: ImageUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const processFile = useCallback(
    async (file: File) => {
      setLocalError(null);

      if (!ACCEPTED_TYPES.includes(file.type)) {
        setLocalError("Only JPEG, PNG, and WebP images are allowed.");
        return;
      }

      if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        setLocalError(`Image must be smaller than ${MAX_FILE_SIZE_MB}MB.`);
        return;
      }

      setProcessing(true);
      try {
        const compressed = await imageCompression(file, {
          maxSizeMB: 0.5,
          maxWidthOrHeight: 1600,
          useWebWorker: true,
          fileType: file.type,
        });

        const base64 = await fileToBase64(compressed);
        if (base64.length > MAX_BASE64_LENGTH) {
          setLocalError("Image is too large after compression. Try a smaller photo.");
          return;
        }

        const previewUrl = URL.createObjectURL(compressed);
        onChange({
          data: base64,
          mime_type: compressed.type || file.type,
          file_name: file.name,
          previewUrl,
        });
      } catch {
        setLocalError("Failed to process image. Please try another file.");
      } finally {
        setProcessing(false);
      }
    },
    [onChange],
  );

  const handleDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      setDragOver(false);
      const file = event.dataTransfer.files[0];
      if (file) {
        void processFile(file);
      }
    },
    [processFile],
  );

  const displayError = error ?? localError;

  return (
    <div className={cn("space-y-3", className)}>
      {value ? (
        <div className="relative overflow-hidden rounded-xl border">
          <img
            src={value.previewUrl}
            alt="Complaint attachment preview"
            className="max-h-64 w-full object-cover"
          />
          <Button
            type="button"
            variant="destructive"
            size="sm"
            className="absolute right-3 top-3"
            onClick={() => onChange(null)}
            aria-label="Remove image"
          >
            <Trash2 className="h-4 w-4" />
            Remove
          </Button>
        </div>
      ) : (
        <div
          role="button"
          tabIndex={0}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === " ") {
              inputRef.current?.click();
            }
          }}
          onDragOver={(event) => {
            event.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={cn(
            "flex cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-8 transition-colors",
            dragOver ? "border-primary bg-primary/5" : "border-muted-foreground/25",
          )}
          aria-label="Upload complaint image"
        >
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
            <ImagePlus className="h-6 w-6 text-primary" />
          </div>
          <div className="text-center">
            <p className="font-medium">Drag & drop an image here</p>
            <p className="mt-1 text-sm text-muted-foreground">
              or click to browse (JPEG, PNG, WebP up to {MAX_FILE_SIZE_MB}MB)
            </p>
          </div>
          <Button type="button" variant="outline" size="sm" disabled={processing}>
            <Upload className="h-4 w-4" />
            {processing ? "Processing..." : "Choose Image"}
          </Button>
        </div>
      )}

      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_TYPES.join(",")}
        className="hidden"
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) {
            void processFile(file);
          }
          event.target.value = "";
        }}
      />

      {displayError ? <p className="text-sm text-destructive">{displayError}</p> : null}
    </div>
  );
}

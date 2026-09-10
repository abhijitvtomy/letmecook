import React, { useRef } from 'react';
import { Camera } from 'lucide-react';

export default function ImageUpload({ onImageSelect, disabled }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      alert("File too large. Max size is 5MB.");
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      onImageSelect(event.target.result);
    };
    reader.readAsDataURL(file);
    e.target.value = null; // reset
  };

  return (
    <div className="flex-shrink-0">
      <input
        type="file"
        accept="image/jpeg, image/png, image/webp"
        className="hidden"
        ref={fileInputRef}
        onChange={handleFileChange}
        disabled={disabled}
      />
      <button
        type="button"
        onClick={() => fileInputRef.current?.click()}
        disabled={disabled}
        className="p-3 text-neutral-400 hover:text-white hover:bg-neutral-700 rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center"
        title="Upload food photo"
      >
        <Camera size={24} />
      </button>
    </div>
  );
}

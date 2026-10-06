import React, { useCallback, useState } from 'react';
import { UploadCloud, X } from 'lucide-react';
import { validateImage } from '../../utils/validators';

const ImageUpload = ({ onImageSelect, currentImage }) => {
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState('');
  const [isDragging, setIsDragging] = useState(false);

  const handleFile = (file) => {
    setError('');
    const validation = validateImage(file);
    if (!validation.valid) {
      setError(validation.message);
      return;
    }

    const objectUrl = URL.createObjectURL(file);
    setPreview(objectUrl);
    onImageSelect(file);
  };

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave') {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const removeImage = () => {
    setPreview(null);
    onImageSelect(null);
    if (preview) {
      URL.revokeObjectURL(preview);
    }
  };

  return (
    <div className="w-full">
      {!preview ? (
        <div
          className={`relative flex flex-col items-center justify-center w-full h-48 border-2 border-dashed rounded-lg cursor-pointer transition-colors ${
            isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50 hover:bg-gray-100'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="flex flex-col items-center justify-center pt-5 pb-6">
            <UploadCloud className="w-10 h-10 mb-3 text-gray-400" />
            <p className="mb-2 text-sm text-gray-500">
              <span className="font-semibold">Click to upload</span> or drag and drop
            </p>
            <p className="text-xs text-gray-500">JPG, JPEG or PNG (MAX. 10MB)</p>
          </div>
          <input 
            type="file" 
            className="hidden" 
            accept="image/jpeg, image/jpg, image/png"
            onChange={handleChange}
            id="image-upload"
          />
          <label htmlFor="image-upload" className="absolute inset-0 cursor-pointer"></label>
        </div>
      ) : (
        <div className="relative w-full h-48 rounded-lg overflow-hidden border border-gray-200">
          <img src={preview} alt="Preview" className="w-full h-full object-cover" />
          <button
            type="button"
            onClick={removeImage}
            className="absolute top-2 right-2 p-1 bg-white rounded-full shadow-md hover:bg-gray-100 text-gray-700"
          >
            <X size={16} />
          </button>
        </div>
      )}
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  );
};

export default ImageUpload;

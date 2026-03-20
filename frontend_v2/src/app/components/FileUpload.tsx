import { Upload, File, X, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { useState } from 'react';

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  status?: 'uploading' | 'success' | 'error';
}

interface FileUploadProps {
  onFilesChange?: (files: UploadedFile[]) => void;
}

export function FileUpload({ onFilesChange }: FileUploadProps) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    processFiles(files);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      processFiles(files);
    }
  };

  const processFiles = async (files: File[]) => {
    const uploadingFiles: UploadedFile[] = files.map(file => ({
      id: Math.random().toString(36).substring(7),
      name: file.name,
      size: file.size,
      status: 'uploading'
    }));
    
    setUploadedFiles(prev => [...prev, ...uploadingFiles]);

    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    try {
      const response = await fetch('http://localhost:8000/upload_pdf', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      setUploadedFiles(prev => prev.map(f => 
        uploadingFiles.find(uf => uf.id === f.id) 
          ? { ...f, status: 'success' } 
          : f
      ));
      
      // Let parent know about the latest successfully uploaded state if needed
      onFilesChange?.(uploadedFiles.concat(uploadingFiles.map(f => ({...f, status: 'success'}))));
    } catch (error) {
      console.error('Error uploading files:', error);
      setUploadedFiles(prev => prev.map(f => 
        uploadingFiles.find(uf => uf.id === f.id) 
          ? { ...f, status: 'error' } 
          : f
      ));
    }
  };

  const removeFile = (id: string) => {
    const updatedFiles = uploadedFiles.filter(file => file.id !== id);
    setUploadedFiles(updatedFiles);
    onFilesChange?.(updatedFiles);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="h-full flex flex-col bg-white border-r border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-gray-900">Documents</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {/* Upload Area */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            isDragging
              ? 'border-blue-600 bg-blue-50'
              : 'border-gray-200 bg-gray-50'
          }`}
        >
          <Upload className={`mx-auto mb-4 ${isDragging ? 'text-blue-600' : 'text-gray-400'}`} size={48} />
          <p className="text-gray-600 mb-2">
            Drag & drop files here
          </p>
          <p className="text-gray-400 mb-4">or</p>
          <label className="inline-block px-4 py-2 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 transition-colors">
            Browse Files
            <input
              type="file"
              multiple
              onChange={handleFileInput}
              className="hidden"
              accept=".pdf,.txt,.doc,.docx,.csv,.json"
            />
          </label>
        </div>

        {/* Uploaded Files List */}
        {uploadedFiles.length > 0 && (
          <div className="mt-6 space-y-2">
            <h3 className="text-gray-700 mb-3">Uploaded Files</h3>
            {uploadedFiles.map(file => (
              <div
                key={file.id}
                className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200 hover:border-blue-600 transition-colors"
              >
                <File className="text-blue-600" size={20} />
                <div className="flex-1 min-w-0">
                  <p className="text-gray-900 truncate">{file.name}</p>
                  <p className="text-gray-400 flex items-center gap-1">
                    {formatFileSize(file.size)}
                    {file.status === 'uploading' && <span className="text-blue-500 text-xs ml-2 flex items-center"><Loader2 size={12} className="animate-spin mr-1"/> Processing...</span>}
                    {file.status === 'success' && <span className="text-green-500 text-xs ml-2 flex items-center"><CheckCircle size={12} className="mr-1"/> Upload Successful</span>}
                    {file.status === 'error' && <span className="text-red-500 text-xs ml-2 flex items-center"><AlertCircle size={12} className="mr-1"/> Failed</span>}
                  </p>
                </div>
                <button
                  onClick={() => removeFile(file.id)}
                  className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <X size={16} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

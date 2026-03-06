import React, { useState } from 'react';
import axios from 'axios';

const FileUpload = () => {
  const [files, setFiles] = useState(null);
  const [status, setStatus] = useState('');

  const handleFiles = (e) => {
    setFiles(e.target.files);
  };

  const upload = async () => {
    if (!files) return;
    const form = new FormData();
    for (let i = 0; i < files.length; i++) {
      form.append('files', files[i]);
    }
    try {
      const res = await axios.post('http://localhost:8000/upload_pdf', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      // if request succeeded, show backend message
      if (res.status === 200) {
        setStatus(res.data.message || 'Upload succeeded');
      } else {
        setStatus(`Upload returned ${res.status}`);
      }
    } catch (err) {
      console.error('upload error', err);
      if (err.response) {
        // server responded with a status outside 2xx
        setStatus(`Upload failed: ${err.response.status} ${err.response.statusText}`);
      } else if (err.request) {
        // request was made but no response
        setStatus('Upload failed: no response from server');
      } else {
        setStatus(`Upload error: ${err.message}`);
      }
    }
  };

  return (
    <div style={{ marginBottom: 20 }}>
      <input type="file" multiple onChange={handleFiles} accept=".pdf" />
      <button onClick={upload}>Upload</button>
      <div>{status}</div>
    </div>
  );
};

export default FileUpload;
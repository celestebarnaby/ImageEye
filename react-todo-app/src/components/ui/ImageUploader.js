import React, { useState } from 'react';

function ImageUploadDialog(props) {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileSelect = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = () => {
    // Handle upload logic here
    // You can use the selectedFile variable to access the file the user selected
  };

  return (
    <div>
      <h2>Upload Image Directory</h2>
      <input type="file" onChange={handleFileSelect} />
      <button onClick={handleUpload}>Upload</button>
    </div>
  );
}

export default ImageUploadDialog;
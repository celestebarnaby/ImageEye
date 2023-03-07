import React, { useState } from 'react';

function FileUploadButton({handleChange}) {
//   const [selectedFiles, setSelectedFiles] = useState(null);

  return (
    <div>
      <input type="file" multiple onChange={handleChange} />
    </div>
  );
}

export default FileUploadButton;
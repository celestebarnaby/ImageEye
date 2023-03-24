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


// import React, { useRef } from 'react'

// const FileUploadButton = (handleChange) => {
//   const ref = useRef();
//   const handleClick = (e) => {
//     ref.current.click()
//   };
//   return (
//     <div>
//       <button onClick={handleClick}>Upload Image</button>
//       <input ref={ref} type="file" />
//     </div>
//   );
// }

// export default FileUploadButton
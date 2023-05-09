import React, { useState } from 'react';
import Sidebar from './Sidebar';
import NewImage from './NewImage';
import SearchResults from './SearchResults';


import Box from '@mui/material/Box';


export function ImageEye({ files, message, updateResults, handleTextChange, handleTextSubmit, handleImageSubmit, searchResults, sidebarFiles, mainImage, changeImage, addObject, addObjectsByName, addImage, removeImage, objectList, annotatedImages, result }) {

  // const [message, setMessage] = useState(message);
  // const [files, setFiles] = useState(files);

  // setFiles(data.files);
  //       setSidebarFiles(data.sidebarFiles);
  //       setMessage(data.message);

  function getAnnotationDescriptions(objs, annotations, annotated) {
    let l = annotated ? annotations : objectList;
    return l.map(i => [objs[i]["Description"], objs[i]["ObjPosInImgLeftToRight"]]);
  }


  return (
    <Box sx={{ display: "flex", flexDirection: "row", height: "100%" }}>
      <Sidebar
        imgsToAnnotate={sidebarFiles}
        allFiles={files}
        changeImage={changeImage}
        handleTextChange={handleTextChange}
        handleTextSubmit={handleTextSubmit}
        annotatedImgs={Object.keys(annotatedImages)}
        updateResults={updateResults}
      />
      <Box sx={{ flex: 1 }}>
        <NewImage
          image={mainImage}
          handleImageSubmit={handleImageSubmit}
        />
      </Box>
      <SearchResults files={searchResults} changeImage={changeImage} result={result} />


    </Box>
  );
}
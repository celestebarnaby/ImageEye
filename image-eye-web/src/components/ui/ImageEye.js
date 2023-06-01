import React, { useState } from 'react';
import Sidebar from './Sidebar';
import NewImage from './NewImage';
import SearchResults from './SearchResults';
import SavedImages from './SavedImages';


import Box from '@mui/material/Box';


export function ImageEye({ files, message, updateResults, handleTextChange, handleTextSubmit, searchResults, sidebarFiles, mainImage, changeImage, addObject, addObjectsByName, addImage, removeImage, objectList, annotatedImages, result, submitSavedImages, handleSavedImages, addToSavedImages, savedImages }) {

  // const [message, setMessage] = useState(message);
  // const [files, setFiles] = useState(files);

  // setFiles(data.files);
  //       setSidebarFiles(data.sidebarFiles);
  //       setMessage(data.message);

  const imgSaved = savedImages.includes(mainImage);

  function getAnnotationDescriptions(objs, annotations, annotated) {
    let l = annotated ? annotations : objectList;
    return l.map(i => [objs[i]["Description"], objs[i]["ObjPosInImgLeftToRight"]]);
  }


  return (
    <Box sx={{ display: "flex", flexDirection: "row", height: "80%" }}>
      <Sidebar
        imgsToAnnotate={sidebarFiles}
        allFiles={files}
        changeImage={changeImage}
        handleTextChange={handleTextChange}
        handleTextSubmit={handleTextSubmit}
        annotatedImgs={Object.keys(annotatedImages)}
        updateResults={updateResults}
        savedImages={savedImages}
      />
      {/* <Box sx={{ flex: 1 }}> */}
      <Box sx={{ flex: 1, overflow: "scroll" }}>
        <NewImage
          image={mainImage}
          annotatedImgs={annotatedImages}
          imgToEnvironment={message}
          addObject={addObject}
          addObjectsByName={addObjectsByName}
          addImage={addImage}
          removeImage={removeImage}
          getAnnotationDescriptions={getAnnotationDescriptions}
          objectList={objectList}
          changeImage={changeImage}
          updateResults={updateResults}
          imgSaved={imgSaved}
          handleSavedImages={handleSavedImages}
        />
      </Box>
      <SearchResults files={searchResults} changeImage={changeImage} result={result} exampleImages={Object.keys(annotatedImages)} updateResults={updateResults} addToSavedImages={addToSavedImages} savedImages={savedImages} />
      <SavedImages images={savedImages} changeImage={changeImage} submitSavedImages={submitSavedImages} />

    </Box>
  );
}
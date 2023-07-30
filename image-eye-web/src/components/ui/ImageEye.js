import React, { useState } from 'react';
import Sidebar from './Sidebar';
import NewImage from './NewImage';
import SearchResults from './SearchResults';
import SavedImages from './SavedImages';


import Box from '@mui/material/Box';


export function ImageEye({ files, message, updateResults, handleTextChange, handleTextSubmit, searchResults, sidebarFiles, mainImage, changeImage, setHighlightedObject, addImage, removeImage, highlightedObject, exampleImages, result, submitSavedImages, handleSavedImages, addToSavedImages, savedImages, robotText, robotText2, setSavedImages, handleTaggingTextChange, handleTaggingTextSubmit, selectedObject, setSelectedObject, tags }) {

  // const [message, setMessage] = useState(message);
  // const [files, setFiles] = useState(files);

  // setFiles(data.files);
  //       setSidebarFiles(data.sidebarFiles);
  //       setMessage(data.message);

  const imgSaved = savedImages.includes(mainImage);

  function getAnnotationDescription(objs, i) {
    return objs[i]["Description"]
    // let l = annotated ? annotations : objectList;
    // return l.map(i => [objs[i]["Description"], objs[i]["ObjPosInImgLeftToRight"]]);
  }


  return (
    <Box sx={{ display: "flex", flexDirection: "row", height: "80%" }}>
      <Sidebar
        allFiles={files}
        changeImage={changeImage}
        handleTextChange={handleTextChange}
        handleTextSubmit={handleTextSubmit}
        exampleImages={exampleImages}
        updateResults={updateResults}
        savedImages={savedImages}
        tags={tags}
      />
      {/* <Box sx={{ flex: 1 }}> */}
      <Box sx={{ flex: 1, overflow: "scroll" }}>
        <NewImage
          image={mainImage}
          exampleImages={exampleImages}
          imgToEnvironment={message}
          setHighlightedObject={setHighlightedObject}
          addImage={addImage}
          removeImage={removeImage}
          getAnnotationDescription={getAnnotationDescription}
          highlightedObject={highlightedObject}
          changeImage={changeImage}
          updateResults={updateResults}
          imgSaved={imgSaved}
          handleSavedImages={handleSavedImages}
          handleTaggingTextChange={handleTaggingTextChange}
          handleTaggingTextSubmit={handleTaggingTextSubmit}
          selectedObject={selectedObject}
          setSelectedObject={setSelectedObject}
          tags={tags}
        />
      </Box>
      <SearchResults files={searchResults} changeImage={changeImage} result={result} exampleImages={Object.keys(exampleImages)} updateResults={updateResults} addToSavedImages={addToSavedImages} savedImages={savedImages} robotText={robotText} robotText2={robotText2} />
      <SavedImages images={savedImages} changeImage={changeImage} submitSavedImages={submitSavedImages} setSavedImages={setSavedImages} />

    </Box>
  );
}
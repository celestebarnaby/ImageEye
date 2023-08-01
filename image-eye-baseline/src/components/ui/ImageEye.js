import React, { useState } from 'react';
import Sidebar from './Sidebar';
import NewImage from './NewImage';
import SearchResults from './SearchResults';
import SavedImages from './SavedImages';


import Box from '@mui/material/Box';


export function ImageEye({ files, handleTextChange, handleTextSubmit, handleImageSubmit, searchResults, sidebarFiles, mainImage, changeImage, handleSavedImages, submitSavedImages, savedImages, addToSavedImages, setSavedImages }) {

  const imgSaved = savedImages.includes(mainImage);

  return (
    <Box sx={{ display: "flex", flexDirection: "row", height: "100%" }}>
      <Sidebar
        imgsToAnnotate={sidebarFiles}
        allFiles={files}
        changeImage={changeImage}
        handleTextChange={handleTextChange}
        handleTextSubmit={handleTextSubmit}
        savedImages={savedImages}
      />
      <Box sx={{ flex: 1, overflow: "scroll", height: "80%" }}>
        <NewImage
          image={mainImage}
          handleImageSubmit={handleImageSubmit}
          handleSavedImages={handleSavedImages}
          imgSaved={imgSaved}
        />
      </Box>
      <SearchResults files={searchResults} changeImage={changeImage} addToSavedImages={addToSavedImages} savedImages={savedImages} />
      <SavedImages images={savedImages} changeImage={changeImage} submitSavedImages={submitSavedImages} setSavedImages={setSavedImages} />
    </Box>
  );
}
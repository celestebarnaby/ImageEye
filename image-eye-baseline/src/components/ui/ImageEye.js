import React, { useState } from 'react';
import Sidebar from './Sidebar';
import NewImage from './NewImage';
import SearchResults from './SearchResults';
import SavedImages from './SavedImages';


import Box from '@mui/material/Box';


export function ImageEye({ files, handleTextChange, handleTextSubmit, handleImageSubmit, searchResults, sidebarFiles, mainImage, changeImage, handleSearchResults, submitResults }) {

  const imgInResults = searchResults.includes(mainImage);

  return (
    <Box sx={{ display: "flex", flexDirection: "row", height: "100%" }}>
      <Sidebar
        imgsToAnnotate={sidebarFiles}
        allFiles={files}
        changeImage={changeImage}
        handleTextChange={handleTextChange}
        handleTextSubmit={handleTextSubmit}
      />
      <Box sx={{ flex: 1 }}>
        <NewImage
          image={mainImage}
          handleImageSubmit={handleImageSubmit}
          handleSearchResults={handleSearchResults}
          imgInResults={imgInResults}
        />
      </Box>
      <SearchResults files={searchResults} changeImage={changeImage} submitResults={submitResults} />

      {/* <SavedImages /> */}
    </Box>
  );
}
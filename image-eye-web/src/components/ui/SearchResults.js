import React, { useState } from 'react';
import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import { Divider, TextField } from '@mui/material';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import AddIcon from '@mui/icons-material/Add';
import IconButton from '@mui/material/IconButton';

function SearchResults({ files, changeImage, result, exampleImages, updateResults, addToSavedImages, savedImages, robotText, robotText2 }) {
  return (
    <Box sx={{ height: "100%", paddingBottom: "5%" }} className="sidebar">
      <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "center" }}>
        <h3>Search Results</h3>
        <IconButton onClick={() => addToSavedImages(files)}><AddIcon /></IconButton>
      </div>
      {files.length > 0 ?
        <Box sx={{ height: "auto" }}>
          <div class="side-by-side">
            <SmartToyIcon fontSize='large' sx={{ marginRight: "10px" }} />
            <SpeechBubble
              text={robotText}
            />
          </div>
          {robotText2 ? <div class="side-by-side">
            <SmartToyIcon fontSize='large' sx={{ marginRight: "10px" }} />
            <SpeechBubble
              text={robotText2}
            />
          </div> : <div></div>}

          <ImageList sx={{ margin: "8px", width: "100%", height: "calc(100% - 76px)" }} cols={3} rowHeight={164}>
            {files.map(img => {
              let class_name = savedImages.includes(img) ? "grayed-out" : "";
              return <ImageListItem key={img} onClick={() => changeImage(img)}>
                <img
                  src={`${img.replace("image-eye-web/public/", "./")}`}
                  className={class_name}
                  loading="lazy"
                />
              </ImageListItem>
            })}

          </ImageList>
        </Box> : <div class="side-by-side">
          <SmartToyIcon fontSize='large' sx={{ marginRight: "10px" }} />
          <SpeechBubble
            text={robotText}
          />
        </div>
      }
    </Box>
  );
}

const SpeechBubble = ({ text }) => {
  return (
    <div className="speech-bubble">
      {text}
    </div>
  );
}

export default SearchResults;
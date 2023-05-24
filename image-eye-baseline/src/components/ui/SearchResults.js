import React, { useState } from 'react';
import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import AddIcon from '@mui/icons-material/Add';

function SearchResults({ files, changeImage, addToSavedImages }) {

  return (
    <Box sx={{ height: "80%" }} className="sidebar">
      <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "center" }}>
        <h3>Search Results</h3>
        <IconButton onClick={() => addToSavedImages(files)}><AddIcon /></IconButton>
      </div>
      {files.length > 0 ?
        // <div>
        <Box sx={{ height: "92%" }}>
          <ImageList sx={{ margin: "8px", width: "100%", height: "100%" }} cols={2} rowHeight={124}>
            {files.map(img => {
              return <ImageListItem key={img} onClick={() => changeImage(img)}>
                <img
                  src={`${img.replace("image-eye-web/public/", "./")}`}
                  loading="lazy"
                />
              </ImageListItem>
            })}

          </ImageList>
        </Box> : <Typography sx={{ paddingLeft: "20px" }}>Enter text query or select similar image to start search.</Typography>}

    </Box>
  );
}

export default SearchResults;
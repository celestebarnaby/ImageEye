import React, { useState } from 'react';
import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import { Divider } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import IconButton from '@mui/material/IconButton';

function SearchResults({ files, changeImage, result, exampleImages, updateResults, addToSavedImages, savedImages }) {

  return (
    <Box sx={{ height: "100%", paddingBottom: "5%" }} className="sidebar">
      {/* <h3>Annotated Images</h3>
      {exampleImages.length > 0 ?
        <Box sx={{ paddingRight: "30px", height: "auto" }}>
          <ImageList sx={{ margin: "8px", width: "100%", height: "calc(100% - 76px)" }} cols={3} rowHeight={164}>
            {exampleImages.map(img => {
              return <ImageListItem key={img} onClick={() => changeImage(img)}>
                <img
                  src={`${img.replace("image-eye-web/public/", "./")}`}
                  loading="lazy"
                />
              </ImageListItem>
            })}
          </ImageList>
          <Button fullWidth variant="contained" onClick={() => updateResults()}>Filter Images by Annotations</Button>
        </Box> : <div></div>
      }
      <Divider></Divider> */}
      <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "center" }}>
        <h3>Search Results</h3>
        <IconButton onClick={() => addToSavedImages(files)}><AddIcon /></IconButton>
      </div>
      {files.length > 0 ?
        <Box sx={{ height: "auto" }}>
          <Typography sx={{ paddingLeft: "20px" }}>{result}</Typography>
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
        </Box> : <Typography sx={{ paddingLeft: "20px" }}>Enter text query or annotate image to start search.</Typography>}
    </Box>
  );
}

export default SearchResults;
import React, { useState } from 'react';
import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import { Divider } from '@mui/material';

function SearchResults({ files, changeImage, result, submitResults, exampleImages, updateResults }) {

  return (
    <Box className="search-results">
      <h3>Example Images</h3>
      {exampleImages.length > 0 ?
        <Box sx={{ paddingRight: "30px", height: "auto" }}>
          <ImageList sx={{ margin: "8px", width: "100%", height: "calc(100% - 76px)" }} cols={2} rowHeight={124}>
            {exampleImages.map(img => {
              return <ImageListItem key={img} onClick={() => changeImage(img)}>
                <img
                  src={`${img.replace("image-eye-web/public/", "./")}`}
                  loading="lazy"
                />
              </ImageListItem>
            })}
          </ImageList>
          <Button fullWidth variant="contained" onClick={() => updateResults()}>Filter images by examples</Button>
        </Box> : <div></div>
      }
      <Divider></Divider>
      <h3>Saved Images</h3>
      {files.length > 0 ?
        <Box sx={{ height: "auto" }}>
          <Typography sx={{ paddingLeft: "20px" }}>{result}</Typography>
          <ImageList sx={{ margin: "8px", width: "100%", height: "calc(100% - 76px)" }} cols={2} rowHeight={124}>
            {files.map(img => {
              return <ImageListItem key={img} onClick={() => changeImage(img)}>
                <img
                  src={`${img.replace("image-eye-web/public/", "./")}`}
                  loading="lazy"
                />
              </ImageListItem>
            })}

          </ImageList>
          <Button sx={{
            margin: "20px", color: "#fff", background: "#1976D2", '&:hover': {
              backgroundColor: '#305fc4'
            },
          }} fullWidth onClick={() => submitResults()}>Submit Images</Button>
        </Box> : <Typography sx={{ paddingLeft: "20px" }}>Enter text query or annotate image to start search.</Typography>}
    </Box>
  );
}

export default SearchResults;
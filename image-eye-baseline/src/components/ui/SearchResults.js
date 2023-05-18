import React, { useState } from 'react';
import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';

function SearchResults({ files, changeImage, submitResults }) {

  return (
    <Box sx={{ height: "100%" }} className="sidebar">
      <h3>Saved Images</h3>
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
          <Button sx={{
            margin: "auto", backgroundColor: "#D27519", color: "#fff", '&:hover': {
              backgroundColor: '#e8933e'
            },
          }} fullWidth onClick={() => submitResults()}>Submit Results</Button>
        </Box> : <Typography sx={{ paddingLeft: "20px" }}>Enter text query or select similar image to start search.</Typography>}
      {/* <Button sx={{
            margin: "auto", backgroundColor: "#D27519", color: "#fff", '&:hover': {
              backgroundColor: '#e8933e', padding: "20px"
            },
          }} fullWidth onClick={() => submitResults()}>Submit Results</Button>
        </div>  */}

    </Box>
  );
}

export default SearchResults;
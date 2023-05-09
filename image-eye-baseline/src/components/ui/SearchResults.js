import React, { useState } from 'react';
import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

function SearchResults({ files, changeImage, result }) {

  return (
    <Box className="search-results">
      <h3>Search Results</h3>
      {files ?
        <div>
          <Typography sx={{ paddingLeft: "20px" }}>{result}</Typography>
          <ImageList sx={{ margin: "8px", width: "calc(100% - 16px)", height: "calc(100% - 76px)" }} cols={2} rowHeight={124}>
            {files.map(img => {
              return <ImageListItem key={img} onClick={() => changeImage(img)}>
                <img
                  src={`${img.replace("image-eye-web/public/", "./")}`}
                  loading="lazy"
                />
              </ImageListItem>
            })}

          </ImageList> </div> : <Typography sx={{ paddingLeft: "20px" }}>Enter text query or show example images to start search.</Typography>}
    </Box>
  );
}

export default SearchResults;
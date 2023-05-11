import React, { useState } from 'react';
import Box from '@mui/material/Box';

import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Divider from '@mui/material/Divider';


function Sidebar({ allFiles, changeImage, handleTextChange, handleTextSubmit }) {

    return (
        <Box sx={{ height: "100%" }} className="sidebar">
            <TextField
                fullWidth
                id="outlined-name"
                label="Describe images to search"
                variant="outlined"
                sx={{ background: "white" }}
                onChange={handleTextChange}
            />
            <Button sx={{
                marginTop: 1, marginBottom: 1, backgroundColor: "#D27519", '&:hover': {
                    backgroundColor: '#e8933e'
                },
            }} fullWidth variant="contained" onClick={handleTextSubmit}>Search by Text</Button>
            <Divider />
            {AllImages(allFiles, changeImage)}
        </Box>
    );
}

function AllImages(allFiles, changeImage) {
    return <ImageList sx={{ width: "100%", height: "87%" }} cols={3} rowHeight={164}>
        {allFiles.map(img => {
            return <ImageListItem key={img} onClick={() => changeImage(img)}>
                <img
                    src={`${img.replace("image-eye-web/public/", "./")}`}
                    loading="lazy"
                />
            </ImageListItem>
        })}
    </ImageList>
}

export default Sidebar;
import React, { useState } from 'react';
import Box from '@mui/material/Box';

import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Divider from '@mui/material/Divider';


function Sidebar({ allFiles, changeImage, handleTextChange, handleTextSubmit, savedImages }) {

    return (
        <Box sx={{ height: "80%" }} className="sidebar">
            <TextField
                fullWidth
                id="outlined-name"
                label="Describe images to search"
                variant="outlined"
                sx={{ background: "white" }}
                onChange={handleTextChange}
                autoComplete='off'
            />
            <Button sx={{
                marginTop: 1, marginBottom: 1, backgroundColor: "#D27519", '&:hover': {
                    backgroundColor: '#e8933e'
                },
            }} fullWidth variant="contained" onClick={handleTextSubmit}>Search by Text</Button>
            <Divider />
            {AllImages(allFiles, changeImage, savedImages)}
        </Box>
    );
}

function AllImages(allFiles, changeImage, savedImages) {
    return <ImageList sx={{ width: "100%", height: "87%" }} cols={3} rowHeight={164}>
        {allFiles.map(img => {
            let class_name = savedImages.includes(img) ? "grayed-out" : "";
            return <ImageListItem key={img} onClick={() => changeImage(img)}>
                <img
                    src={`${img.replace("image-eye-web/public/", "./")}`}
                    loading="lazy"
                    className={class_name}
                />
            </ImageListItem>
        })}
    </ImageList>
}

export default Sidebar;
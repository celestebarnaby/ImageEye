import React, { useState } from 'react';
import ImageMapper from 'react-img-mapper';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';

export default function NewImage({ image, handleImageSubmit, handleSavedImages, imgSaved }) {

    let img_dir = image ? image : null;

    const new_width = 500;

    return (
        <div>
            <Box className="image-container">
                {image && Image(image, new_width, handleImageSubmit, handleSavedImages, img_dir, imgSaved)}
            </Box>
        </div>
    );
}



function Image(image, new_width, handleImageSubmit, handleSavedImages, img_dir, imgSaved) {

    const icon = imgSaved ? <RemoveIcon /> : <AddIcon />;

    return <Box>
        {/* <img src={require(image)} className="center-image"/> */}
        <IconButton sx={{ marginLeft: "auto", display: "flex" }} onClick={() => handleSavedImages(img_dir, true)}>{icon}</IconButton>
        <ImageMapper src={image.replace("image-eye-web/public/", "./")} toggleHighlighted={true} stayMultiHighlighted={true} width={new_width} />
        <Box className="buttons-container">
            <Button sx={{
                margin: "auto", backgroundColor: "#D27519", color: "#fff", '&:hover': {
                    backgroundColor: '#e8933e'
                },
            }} onClick={() => handleImageSubmit(img_dir)}>Search for Similar Images</Button>
            {/* <Button sx={{
                margin: "auto", backgroundColor: "#D27519", color: "#fff", '&:hover': {
                    backgroundColor: '#e8933e'
                },
            }} onClick={() => handleSearchResults(img_dir)}>{button_text}</Button> */}
        </Box>
    </Box>
}



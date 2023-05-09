import React, { useState } from 'react';
import ImageMapper from 'react-img-mapper';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';

export default function NewImage({ image, handleImageSubmit, handleSearchResults, imgInResults }) {


    let img_dir = image ? image : null;

    const new_width = 500;

    return (
        <div>
            <Box className="image-container">
                {image && Image(image, new_width, handleImageSubmit, handleSearchResults, img_dir, imgInResults)}
            </Box>
        </div>
    );
}



function Image(image, new_width, handleImageSubmit, handleSearchResults, img_dir, imgInResults) {

    const button_text = imgInResults ? "Remove from Search Results" : "Add to Search Results";

    return <Box>
        {/* <img src={require(image)} className="center-image"/> */}
        <ImageMapper src={image.replace("image-eye-web/public/", "./")} toggleHighlighted={true} stayMultiHighlighted={true} width={new_width} />
        <Box className="buttons-container">
            <Button sx={{ margin: "auto", backgroundColor: "#D27519", color: "#fff" }} onClick={() => handleImageSubmit(img_dir)}>Search for Similar Images</Button>
            <Button sx={{ margin: "auto", backgroundColor: "#D27519", color: "#fff" }} onClick={() => handleSearchResults(img_dir)}>{button_text}</Button>
        </Box>
    </Box>
}



import React, { useState } from 'react';
import ImageMapper from 'react-img-mapper';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import { Divider } from '@mui/material';
import IconButton from '@mui/material/IconButton';
import DeleteIcon from '@mui/icons-material/Delete';
import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import { alignProperty } from '@mui/material/styles/cssUtils';

export default function NewImage({ image, handleImageSubmit }) {


    let img_dir = image ? image : null;

    const new_width = 500;

    return (
        <div>
            <Box className="image-container">
                {image && Image(image, new_width, handleImageSubmit, img_dir,)}
            </Box>
        </div>
    );
}



function Image(image, new_width, handleImageSubmit, img_dir) {
    return <Box>
        {/* <img src={require(image)} className="center-image"/> */}
        <ImageMapper src={image.replace("image-eye-web/public/", "./")} toggleHighlighted={true} stayMultiHighlighted={true} width={new_width} />
        <Box className="buttons-container">
            <Button sx={{ margin: "auto" }} variant="outlined" onClick={() => handleImageSubmit(img_dir)}>Search for Similar Images</Button>
        </Box>
    </Box>
}



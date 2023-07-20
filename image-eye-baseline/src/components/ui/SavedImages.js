import React from 'react';
import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import { Typography } from '@mui/material';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import Button from '@mui/material/Button';
import KeyboardDoubleArrowRightIcon from '@mui/icons-material/KeyboardDoubleArrowRight';

export default function SavedImages({ images, changeImage, submitSavedImages }) {
    return (
        <div class="footer">
            <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "center" }}>
                <Typography>Saved Images</Typography>
                <IconButton sx={{ color: "white" }} onClick={() => submitSavedImages()}><KeyboardDoubleArrowRightIcon /></IconButton>
                <Button sx={{
                    color: "#fff", '&:hover': {
                        backgroundColor: 'orange'
                    },
                }} onClick={() => setSavedImages([])}>{"Clear"}</Button>
            </div>
            <ImageList
                sx={{
                    gridAutoFlow: "column",
                    gridTemplateColumns: "repeat(auto-fill,minmax(60px,1fr)) !important",
                    gridAutoColumns: "minmax(60px, 1fr)",
                    padding: "0px",
                    margin: "0px",
                    marginLeft: "10px",
                    paddingRight: "10px",
                }}
            >
                {images.map((image) => (
                    <ImageListItem sx={{ padding: "0px" }} key={image} onClick={() => changeImage(image)}>
                        <img src={`${image.replace("image-eye-web/public/", "./")}`} />
                        {/* <ImageListItemBar title={"hi"} /> */}
                    </ImageListItem>
                ))}
            </ImageList>
        </div>
    );
};

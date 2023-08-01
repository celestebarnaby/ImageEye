import React, { useState } from 'react';
import Box from '@mui/material/Box';

import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';


export function SubmittedResults({ savedImages }) {

    return (
        <div>
            <h3 style={{ padding: "20px" }}>Results Submitted</h3>
            <Box sx={{ display: "flex", flexDirection: "row", height: "100%" }}>
                <ImageList sx={{ margin: "8px", width: "80%", height: "100%" }} cols={4} >
                    {savedImages.map(img => {
                        return <ImageListItem key={img} onClick={() => changeImage(img)}>
                            <img
                                src={`${img.replace("image-eye-web/public/", "./")}`}
                                loading="lazy"
                            />
                        </ImageListItem>
                    })}
                </ImageList>
            </Box>
        </div>
    );
}
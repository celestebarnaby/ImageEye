import React, { useState } from 'react';
import Box from '@mui/material/Box';

import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Divider from '@mui/material/Divider';


function Sidebar({ allFiles, imgsToAnnotate, changeImage, savedImages, handleTextChange, handleTextSubmit, updateResults }) {

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
            <Button sx={{ marginTop: 1 }} fullWidth variant="contained" onClick={handleTextSubmit}>Sort images by description</Button>
            <Divider />
            {AllImages(allFiles, savedImages, changeImage)}
        </Box>
    );
}

// function AnnotationSuggestions(imgsToAnnotate, savedImages, changeImage) {
//     return <div>
//         <ul>
//             {imgsToAnnotate ?
//                 imgsToAnnotate.map(img => <li><img className={savedImages.includes(img) ? "small-img-grayed-out" : "small-img"}
//                     src={img.replace("image-eye-web/public/", "./")} key="{img}" onClick={() => changeImage(img)} /></li>)
//                 : <p>Enter text query to get annotation suggestions.</p>
//             }
//         </ul>
//     </div>
// }

function AllImages(allFiles, savedImages, changeImage) {
    // let height = imgsToAnnotate.length > 0 ? 200 : 0;

    return <ImageList sx={{ width: "100%", height: "87%" }} cols={3} rowHeight={164}>
        {allFiles.map(img => {
            let class_name = savedImages.includes(img) ? "grayed-out" : "";
            return <ImageListItem key={img} onClick={() => changeImage(img)}>
                <img
                    src={`${img.replace("image-eye-web/public/", "./")}`}
                    className={class_name}
                    loading="lazy"
                />
            </ImageListItem>
        })}
    </ImageList>
}

{/* {imgsToAnnotate.length > 0 ? <h3>Recommended images to annotate</h3> : <></>}
        <ImageList sx={{ width: "100%", height: height }} cols={3} rowHeight={164}>
            {imgsToAnnotate.length > 0 ?
                imgsToAnnotate.map(img => {
                    let class_name = savedImages.includes(img) ? "grayed-out" : "";
                    return <ImageListItem key={img} onClick={() => changeImage(img)}>
                        <img
                            src={`${img.replace("image-eye-web/public/", "./")}`}
                            className={class_name}
                            loading="lazy"
                        />
                    </ImageListItem>
                }) : <></>}
        </ImageList>
        {imgsToAnnotate.length > 0 ? <hr /> : <></>} */}
{/* {allFiles ? <h3>All Images</h3> : {}} */ }

export default Sidebar;
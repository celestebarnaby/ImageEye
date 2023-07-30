import React, { useState } from 'react';
import Box from '@mui/material/Box';

import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Divider from '@mui/material/Divider';


function Sidebar({ allFiles, changeImage, savedImages, handleTextChange, handleTextSubmit, exampleImages, tags }) {

    return (
        <Box sx={{ height: "100%" }} className="sidebar">
            <Button sx={{ marginTop: 1, marginBottom: 1 }} fullWidth variant="contained" onClick={handleTextSubmit}>Search </Button>
            <TextField
                fullWidth
                id="outlined-name"
                label="Describe images to search"
                variant="outlined"
                sx={{ background: "white" }}
                onChange={handleTextChange}
                autoComplete='off'
            />
            <h3>Example Images</h3>
            {Object.keys(exampleImages).length > 0 ?
                <Box sx={{ paddingRight: "30px", height: "auto" }}>
                    <ImageList sx={{ margin: "8px", width: "100%", height: "calc(100% - 76px)" }} cols={3} rowHeight={164}>
                        {Object.keys(exampleImages).map(img => {
                            let class_name = exampleImages[img] ? "example-img-pos" : "example-img-neg";
                            return <ImageListItem key={img} onClick={() => changeImage(img)}>
                                <img className={class_name}
                                    src={`${img.replace("image-eye-web/public/", "./")}`}
                                    loading="lazy"
                                />
                            </ImageListItem>
                        })}
                    </ImageList>
                </Box> : <div>Add example images to refine search.</div>
            }
            {/* {Object.keys(tags).length > 0 ?
                <Box sx={{ paddingRight: "30px", height: "auto" }}>
                    <h3>Tagged Faces</h3>
                    <List sx={{ margin: "8px", width: "100%", height: "calc(100% - 76px)" }} cols={3} rowHeight={164}>
                        {Object.values(tags).map((tag) => {
                            return tag["text"]
                        })}
                    </List>
                </Box> : <div />
            } */}
            <Divider></Divider>
            {/* <Divider /> */}
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
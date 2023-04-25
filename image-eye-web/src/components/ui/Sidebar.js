import React, { useState } from 'react';
import Box from '@mui/material/Box';

import ImageList from '@mui/material/ImageList';
import ImageListItem from '@mui/material/ImageListItem';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Divider from '@mui/material/Divider';


function Sidebar({ allFiles, imgsToAnnotate, changeImage, annotatedImgs, handleTextChange, handleTextSubmit, updateResults }) {
    const [selectedTab, setSelectedTab] = useState("tab1");

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
            <Button sx={{ marginTop: 1, marginBottom: 1 }} fullWidth variant="contained" onClick={handleTextSubmit}>Filter images by description</Button>
            <Divider />
            <div className="side-by-side">
                <button className="button-12" onClick={() => setSelectedTab("tab1")}>All Images</button>
                <button className="button-12" onClick={() => setSelectedTab("tab2")}>Images to Annotate</button>
                <button className="button-12" onClick={() => setSelectedTab("tab3")}>Annotated Images</button>
            </div>
            <div>
                {selectedTab === "tab2" ? AnnotationSuggestions(imgsToAnnotate, annotatedImgs, changeImage) :
                    (selectedTab === "tab1" ? AllImages(allFiles, annotatedImgs, changeImage) :
                        AnnotatedImages(allFiles, annotatedImgs, changeImage))}
            </div>
            <Box>
                <Button variant="contained" fullWidth onClick={() => updateResults(annotatedImgs)}>Filter images by example</Button>
            </Box>
        </Box>
    );
}

function AnnotationSuggestions(imgsToAnnotate, annotatedImgs, changeImage) {
    return <div>
        <ul>
            {imgsToAnnotate ?
                imgsToAnnotate.map(img => <li><img className={annotatedImgs.includes(img) ? "small-img-grayed-out" : "small-img"}
                    src={img.replace("image-eye-web/public/", "./")} key="{img}" onClick={() => changeImage(img)} /></li>)
                : <p>Enter text query to get annotation suggestions.</p>
            }
        </ul>
    </div>
}

function AllImages(allFiles, annotatedImgs, changeImage) {
    // console.log(allFiles);

    return <ImageList sx={{ width: "100%", height: 600 }} cols={3} rowHeight={164}>
        {allFiles ?
            allFiles.map(img => {
                return <ImageListItem key={img} onClick={() => changeImage(img)}>
                    <img
                        src={`${img.replace("image-eye-web/public/", "./")}`}
                        loading="lazy"
                    />
                </ImageListItem>
            })
            : <p>Enter text query to get annotation suggestions.</p>
        }
    </ImageList>
}

function AnnotatedImages(allFiles, annotatedImgs, changeImage) {
    return <div>
        <ul>
            {allFiles ?
                allFiles.filter(img => annotatedImgs.includes(img)).map(img => <li><img className={"small-img"}
                    src={img.replace("image-eye-web/public/", "./")} key="{img}" onClick={() => changeImage(img)} /></li>)
                : <p>Annotated images will be listed here.</p>
            }
        </ul>
    </div>
}

export default Sidebar;
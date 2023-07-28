import React, { useState } from 'react';
import ImageMapper from 'react-img-mapper';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import TextField from '@mui/material/TextField';

export default function NewImage({ image, imgToEnvironment, exampleImages, setHighlightedObject, highlightedObject, addImage, removeImage, imgSaved, handleSavedImages, handleTaggingTextChange, handleTaggingTextSubmit, selectedObject, setSelectedObject, tags }) {

    let img_dir = image ? image : null;

    let annotated = Object.keys(exampleImages).includes(img_dir)
    let annotations = annotated ? exampleImages[img_dir] : [];

    const new_width = 500;
    const cur_width = img_dir ? imgToEnvironment[img_dir]['dimensions'][0] : 0;
    const cur_height = img_dir ? imgToEnvironment[img_dir]['dimensions'][1] : 0;
    const new_height = cur_height * (new_width / cur_width);
    let env = img_dir ? imgToEnvironment[img_dir]['environment'] : [];
    let i = -1;
    let objs = Object.values(env);
    objs.sort((a, b) => ((a['Loc'][2] - a['Loc'][0]) * (a['Loc'][3] - a['Loc'][1])) - ((b['Loc'][2] - b['Loc'][0]) * (b['Loc'][3] - b['Loc'][1])))

    // let descs = getDescription(objs, annotations, annotated);
    let desc = highlightedObject !== null ? objs[highlightedObject]["Description"] : "";
    let isFace = selectedObject !== null && objs[selectedObject]["Type"] == "Face";
    let isTagged = isFace && Object.keys(tags).includes(objs[selectedObject]["Index"].toString());



    let areas = objs.map((value) => {
        const curX1 = value['Loc'][0];
        const curY1 = value['Loc'][1];
        const curX2 = value['Loc'][2];
        const curY2 = value['Loc'][3];

        i = i + 1;

        return {
            shape: 'rect',
            coords: [
                curX1 * (new_width / cur_width),
                curY1 * (new_height / cur_height),
                curX2 * (new_width / cur_width),
                curY2 * (new_height / cur_height)
            ],
            id: i,
        };
    });

    const map = {
        name: 'map',
        areas: areas
    };


    return (
        <div>
            <Box className="image-container">
                {image && (
                    annotated ? AnnotatedImage(image, map, setHighlightedObject, new_width, objs, img_dir, removeImage, imgSaved, handleSavedImages, exampleImages, desc) : UnannotatedImage(image, map, setHighlightedObject, new_width, addImage, img_dir, objs, imgSaved, handleSavedImages, desc, setSelectedObject, selectedObject, isFace, handleTaggingTextChange, handleTaggingTextSubmit, isTagged))}
            </Box>
            {/* {ExampleSet(Object.keys(exampleImages), changeImage, updateResults)} */}
        </div>
    );
}


function UnannotatedImage(image, map, setHighlightedObject, new_width, addImage, img_dir, objs, imgSaved, handleSavedImages, desc, setSelectedObject, selectedObject, isFace, handleTaggingTextChange, handleTaggingTextSubmit, isTagged) {
    const icon = imgSaved ? <RemoveIcon /> : <AddIcon />;

    return <Box>
        {/* <img src={require(image)} className="center-image"/> */}
        <div className='side-by-side'>
            {/* <div sx={{ marginBottom: "auto" }}>Select the objects in the image that pertain to your task.</div> */}
            <IconButton onClick={() => handleSavedImages(img_dir, true, true)}>{icon}</IconButton>
        </div>
        <ImageMapper src={image.replace("image-eye-web/public/", "./")} map={map} onMouseLeave={(area, index) => setHighlightedObject(null)} onClick={(area, index) => setSelectedObject(index)} onMouseEnter={(area, index) => setHighlightedObject(index)} toggleHighlighted={true} stayHighlighted={true} width={new_width} />
        <Box className="buttons-container">
            <Button sx={{
                margin: "auto", color: "#fff", background: "#1976D2", '&:hover': {
                    backgroundColor: '#305fc4'
                },
            }} onClick={() => addImage(img_dir, true)}>{"Add Positive Example"}</Button>
            <Button sx={{
                margin: "auto", color: "#fff", background: "#1976D2", '&:hover': {
                    backgroundColor: '#305fc4'
                },
            }} onClick={() => addImage(img_dir, false)}>{"Add Negative Example"}</Button>
        </Box>
        {/* <div style={{ paddingBottom: "25%" }} className="side-by-side"> */}
        <div style={{ marginTop: 10, width: 500 }}>
            <Box sx={{ maxWidth: "400px" }}>
                {desc}
            </Box>
        </div>
        {/* </div> */}
        {isFace ?
            (isTagged ? <Button sx={{ marginTop: 1, marginBottom: 1 }} fullWidth variant="contained" onClick={() => handleTaggingTextSubmit(objs[selectedObject]["Index"], true)}>Remove Tag</Button> : <div>
                <Button sx={{ marginTop: 1, marginBottom: 1 }} fullWidth variant="contained" onClick={() => handleTaggingTextSubmit(objs[selectedObject]["Index"], false)}>Search </Button>
                <TextField
                    fullWidth
                    id="outlined-name"
                    label="Describe images to search"
                    variant="outlined"
                    sx={{ background: "white" }}
                    onChange={handleTaggingTextChange}
                    autoComplete='off'
                />
            </div>) : <div />}
    </Box>
}

function AnnotatedImage(image, map, setHighlightedObject, new_width, objs, img_dir, removeImage, imgSaved, handleSavedImages, exampleImages, desc) {
    const icon = imgSaved ? <RemoveIcon /> : <AddIcon />;
    const text = exampleImages[image] ? "Image has been added as a positive example." : "Image has been added as a negative example.";

    return <Box>
        {/* <img src={require(image)} className="center-image"/> */}
        <div className='side-by-side'>
            <div>{text}</div>
            <IconButton sx={{ marginLeft: "auto" }} onClick={() => handleSavedImages(img_dir, true, true)}>{icon}</IconButton>
        </div>
        <ImageMapper src={image.replace("image-eye-web/public/", "./")} map={map} onMouseLeave={(area, index) => setHighlightedObject(null)} onMouseEnter={(area, index) => setHighlightedObject(objs[index]['ObjPosInImgLeftToRight'])} toggleHighlighted={true} stayMultiHighlighted={true} width={new_width} />
        <Box className="buttons-container">
            {/* <button className="button-10-2">Annotate</button> */}
            <Button sx={{
                margin: "auto", color: "#fff", background: "#1976D2", '&:hover': {
                    backgroundColor: '#305fc4'
                },
            }} variant="outlined" onClick={() => removeImage(img_dir)}>Remove Example</Button>
        </Box>
        <div>
            <Box sx={{ maxWidth: "400px" }}>
                {desc ? desc : "\n\n\n"}
            </Box>
        </div>
    </Box>
}

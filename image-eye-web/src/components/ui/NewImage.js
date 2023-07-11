import React, { useState } from 'react';
import ImageMapper from 'react-img-mapper';
// import ImageMapper2 from './ImageMapper2';
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
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import SaveAltIcon from '@mui/icons-material/SaveAlt';

export default function NewImage({ image, imgToEnvironment, exampleImages, selectObject, selectedObject, addImage, removeImage, objectList, imgSaved, handleSavedImages }) {
    const [hoveredObjectList, setHoveredObjectList] = useState([]);

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
    // let descs = getDescription(objs, annotations, annotated);
    let desc = selectedObject !== null ? objs[selectedObject]["Description"] : "";
    // let object_names = objs.filter(obj => obj["Type"] == "Object").map(obj => obj["Name"]);
    // let type_names = objs.filter(obj => obj["Type"] != "Object").map(obj => obj["Type"]);
    // let full_object_names = [...new Set(object_names.concat(type_names))];
    objs.sort((a, b) => ((a['Loc'][2] - a['Loc'][0]) * (a['Loc'][3] - a['Loc'][1])) - ((b['Loc'][2] - b['Loc'][0]) * (b['Loc'][3] - b['Loc'][1])))

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
            // preFillColor: ((annotated && annotations.includes(objs[i]['ObjPosInImgLeftToRight'])) ? "rgba(255, 100, 255, 0.5)" :
            // (objectList.includes(objs[i]['ObjPosInImgLeftToRight']) || hoveredObjectList.includes(objs[i]['ObjPosInImgLeftToRight']) ? "rgba(255, 255, 255, 0.5)" : undefined)),
            // undefined),
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
                    annotated ? AnnotatedImage(image, map, selectObject, new_width, objs, img_dir, removeImage, imgSaved, handleSavedImages, exampleImages, desc) : UnannotatedImage(image, map, selectObject, new_width, addImage, img_dir, objs, imgSaved, handleSavedImages, desc))}
            </Box>
            {/* {ExampleSet(Object.keys(exampleImages), changeImage, updateResults)} */}
        </div>
    );
}


function UnannotatedImage(image, map, selectObject, new_width, addImage, img_dir, objs, imgSaved, handleSavedImages, desc) {
    const icon = imgSaved ? <RemoveIcon /> : <AddIcon />;

    return <Box>
        {/* <img src={require(image)} className="center-image"/> */}
        <div className='side-by-side'>
            {/* <div sx={{ marginBottom: "auto" }}>Select the objects in the image that pertain to your task.</div> */}
            <IconButton onClick={() => handleSavedImages(img_dir, true)}>{icon}</IconButton>
        </div>
        <ImageMapper src={image.replace("image-eye-web/public/", "./")} map={map} onMouseLeave={(area, index) => selectObject(null)} onMouseEnter={(area, index) => selectObject(objs[index]['ObjPosInImgLeftToRight'])} toggleHighlighted={true} stayMultiHighlighted={true} width={new_width} />
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
            {desc}
        </div>
        {/* </div> */}
    </Box>
}

function AnnotatedImage(image, map, selectObject, new_width, objs, img_dir, removeImage, imgSaved, handleSavedImages, exampleImages, desc) {
    const icon = imgSaved ? <RemoveIcon /> : <AddIcon />;
    const text = exampleImages[image] ? "Image has been added as a positive example." : "Image has been added as a negative example.";

    return <Box>
        {/* <img src={require(image)} className="center-image"/> */}
        <div className='side-by-side'>
            <div>{text}</div>
            <IconButton sx={{ marginLeft: "auto" }} onClick={() => handleSavedImages(img_dir, true)}>{icon}</IconButton>
        </div>
        <ImageMapper src={image.replace("image-eye-web/public/", "./")} map={map} onMouseLeave={(area, index) => selectObject(null)} onMouseEnter={(area, index) => selectObject(objs[index]['ObjPosInImgLeftToRight'])} toggleHighlighted={true} stayMultiHighlighted={true} width={new_width} />
        <Box className="buttons-container">
            {/* <button className="button-10-2">Annotate</button> */}
            <Button sx={{
                margin: "auto", color: "#fff", background: "#1976D2", '&:hover': {
                    backgroundColor: '#305fc4'
                },
            }} variant="outlined" onClick={() => removeImage(img_dir)}>Remove Example</Button>
        </Box>
        <div>
            {desc}
        </div>
    </Box>
}

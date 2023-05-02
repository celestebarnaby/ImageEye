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

export default function NewImage({ image, imgToEnvironment, annotatedImgs, addObject, addObjectsByName, addImage, getAnnotationDescriptions, removeImage, objectList, changeImage, updateResults }) {
    const [hoveredObjectList, setHoveredObjectList] = useState([]);

    let addHoveredObject = (index) => {
        if (hoveredObjectList.includes(index)) {
            const other_index = hoveredObjectList.indexOf(index);
            hoveredObjectList.splice(other_index, 1); // 2nd parameter means remove one item only
        }
        else {
            hoveredObjectList.push(index);
        }
        setHoveredObjectList([...hoveredObjectList]);
    }

    let hoverOverObjects = (name, objs) => {
        if (name != "Face" && name != "Text") {
            let new_indices = objs.filter(obj => obj['Name'] == name).map(obj => obj['ObjPosInImgLeftToRight']);
            new_indices.forEach(index => addHoveredObject(index));
        }
        else {
            let new_indices = objs.filter(obj => obj['Type'] == name).map(obj => obj['ObjPosInImgLeftToRight']);
            new_indices.forEach(index => addHoveredObject(index));
        }
        setHoveredObjectList([...hoveredObjectList]);
    }

    let removeHover = () => {
        setHoveredObjectList([]);
    }

    let img_dir = image ? image : null;

    let annotated = Object.keys(annotatedImgs).includes(img_dir)
    let annotations = annotated ? annotatedImgs[img_dir] : [];

    const new_width = 500;
    const cur_width = img_dir ? imgToEnvironment[img_dir]['dimensions'][0] : 0;
    const cur_height = img_dir ? imgToEnvironment[img_dir]['dimensions'][1] : 0;
    const new_height = cur_height * (new_width / cur_width);
    let env = img_dir ? imgToEnvironment[img_dir]['environment'] : [];
    let i = -1;
    let objs = Object.values(env);
    let descs = getAnnotationDescriptions(objs, annotations, annotated);
    let object_names = objs.filter(obj => obj["Type"] == "Object").map(obj => obj["Name"]);
    let type_names = objs.filter(obj => obj["Type"] != "Object").map(obj => obj["Type"]);
    let full_object_names = [...new Set(object_names.concat(type_names))];
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
            preFillColor: ((annotated && annotations.includes(objs[i]['ObjPosInImgLeftToRight'])) ? "rgba(255, 100, 255, 0.5)" :
                (objectList.includes(objs[i]['ObjPosInImgLeftToRight']) || hoveredObjectList.includes(objs[i]['ObjPosInImgLeftToRight']) ? "rgba(255, 255, 255, 0.5)" : undefined)),
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
                    annotated ? AnnotatedImage(image, map, addObject, new_width, objs, descs, img_dir, removeImage) : UnannotatedImage(image, map, addObject, addObjectsByName, new_width, addImage, img_dir, objs, descs, full_object_names, hoverOverObjects, removeHover))}
            </Box>
            {ExampleSet(Object.keys(annotatedImgs), changeImage, updateResults)}
        </div>
    );
}

function ExampleSet(annotatedImgs, changeImage, updateResults) {
    let height = annotatedImgs.length > 0 ? 200 : 0;
    return <Box sx={{ paddingLeft: "80px", paddingRight: "80px", paddingTop: "20px", display: "auto" }}>
        {annotatedImgs.length > 0 ? <h3>Examples</h3> : <></>}
        <ImageList sx={{ width: "100%", height: height, overflowX: "auto" }} cols={3} rowHeight={164}>
            {annotatedImgs.length > 0 ?
                annotatedImgs.map(img => {
                    return <ImageListItem key={img} onClick={() => changeImage(img)}>
                        <img
                            src={`${img.replace("image-eye-web/public/", "./")}`}
                            loading="lazy"
                        />
                    </ImageListItem>
                }) : <></>}
        </ImageList>
        <Button fullWidth variant="contained" onClick={() => updateResults()}>Filter images by examples</Button>
    </Box>
}

function UnannotatedImage(image, map, addObject, addObjectsByName, new_width, addImage, img_dir, objs, descs, full_object_names, hoverOverObjects, removeHover) {
    return <Box>
        {/* <img src={require(image)} className="center-image"/> */}
        <ImageMapper src={image.replace("image-eye-web/public/", "./")} map={map} onClick={(area, index) => addObject(objs[index]['ObjPosInImgLeftToRight'], true)} toggleHighlighted={true} stayMultiHighlighted={true} width={new_width} />
        <Box className="buttons-container">
            <Button sx={{ margin: "auto" }} variant="outlined" onClick={() => addImage(img_dir)}>Add Example</Button>
        </Box>
        <div className="side-by-side">
            <div>
                <h3>Objects found in image</h3>
                <div style={{ width: "300px" }}>
                    {full_object_names.map(name => <Button sx={{ marginLeft: 1, marginRight: 1, marginTop: 1, marginBottom: 1 }} variant="contained" onClick={() => addObjectsByName(name, objs)} onMouseOver={() => hoverOverObjects(name, objs)} onMouseOut={() => removeHover()}>{name}</Button>)}
                </div>
            </div>
            {/* // onMouseOver={hoverOverObjects(name, objs)} onMouseOut={removeHover()} */}
            <div>
                <h3>Selected Objects</h3>
                <div style={{ height: "200px", overflow: "scroll" }}>
                    <List>
                        {descs.map(desc => <div><ListItem secondaryAction={
                            <IconButton edge="end" aria-label="delete" onClick={() => addObject(desc[1], true)}>
                                <DeleteIcon />
                            </IconButton>
                        }><ListItemText primary={desc[0]} /></ListItem><Divider /></div>)}
                    </List>
                </div>
            </div>
        </div>
    </Box>
}

function AnnotatedImage(image, map, addObject, new_width, objs, descs, img_dir, removeImage) {
    return <Box>
        {/* <img src={require(image)} className="center-image"/> */}
        <Typography>Image has been annotated</Typography>
        <ImageMapper src={image.replace("image-eye-web/public/", "./")} map={map} onClick={(area, index) => addObject(objs[index]['ObjPosInImgLeftToRight'])} width={new_width} />
        <Box className="buttons-container">
            {/* <button className="button-10-2">Annotate</button> */}
            <Button sx={{ margin: "auto" }} variant="outlined" onClick={() => removeImage(img_dir)}>Remove Example</Button>
        </Box>
        <List>
            {descs.map(desc => <div><ListItem><ListItemText primary={desc[0]} /></ListItem><Divider /></div>)}
        </List>
    </Box>
}

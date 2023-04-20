import React from 'react';
import ImageMapper from 'react-img-mapper';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

export default function NewImage({ image, imgToEnvironment, annotatedImgs, addObject, addImage, getAnnotationDescriptions, removeImage }) {
    
    let img_dir = image ? image : null;

    console.log('?????')
    console.log(image)
    console.log(img_dir)
    console.log(imgToEnvironment)

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
            preFillColor: ((annotated && annotations.includes(objs[i]['ObjPosInImgLeftToRight'])) ? "rgba(255, 100, 255, 0.5)" : undefined),
        };
    });

    const map = {
        name: 'map',
        areas: areas
    };


    return (
        <Box className="image-container">
            {image && (
                annotated ? AnnotatedImage(image, map, addObject, new_width, objs, descs, img_dir, removeImage) : UnannotatedImage(image, map, addObject, new_width, addImage, img_dir, objs, descs))}
        </Box>
    );
}

function UnannotatedImage(image, map, addObject, new_width, addImage, img_dir, objs, descs) {
    return <Box>
        {/* <img src={require(image)} className="center-image"/> */}
        <ImageMapper src={image.replace("image-eye-web/public/", "./")} map={map} onClick={(area, index) => addObject(objs[index]['ObjPosInImgLeftToRight'])} toggleHighlighted={true} stayMultiHighlighted={true} width={new_width} />
        <Box className="buttons-container">
            <Button sx={{margin: "auto"}} variant="outlined" onClick={() => addImage(img_dir)}>Add as an annotated example</Button>
        </Box>
        {descs.map(desc => <p>{desc}<br /></p>)}
    </Box>
}

function AnnotatedImage(image, map, addObject, new_width, objs, descs, img_dir, removeImage) {
    return <Box>
        {/* <img src={require(image)} className="center-image"/> */}
        <Typography>Image has been annotated</Typography>
        <ImageMapper src={image.replace("image-eye-web/public/", "./")} map={map} onClick={(area, index) => addObject(objs[index]['ObjPosInImgLeftToRight'])} width={new_width} />
        <Box className="buttons-container">
            {/* <button className="button-10-2">Annotate</button> */}
            <Button sx={{margin: "auto"}} variant="outlined" onClick={() => removeImage(img_dir)}>Remove from the example set</Button>
        </Box>
        {descs.map(desc => <p>{desc}<br /></p>)}
    </Box>
}

import React from 'react';
import ImageMapper from 'react-img-mapper';

export default function NewImage({ image, imgToEnvironment, annotatedImgs, addObject, addImage, getAnnotationDescriptions, removeImage }) {

    let img_dir = image ? "image-search-gui/src/components/ui" + image.slice(1) : null;
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
        <div>
            {image && (
                annotated ? AnnotatedImage(image, map, addObject, new_width, objs, descs, img_dir, removeImage) : UnannotatedImage(image, map, addObject, new_width, addImage, img_dir, objs, descs))}
        </div>
    );
}

function UnannotatedImage(image, map, addObject, new_width, addImage, img_dir, objs, descs) {
    return <div className="image-container">
        {/* <img src={require(image)} className="center-image"/> */}
        <ImageMapper src={require(image)} map={map} onClick={(area, index) => addObject(objs[index]['ObjPosInImgLeftToRight'])} toggleHighlighted={true} stayMultiHighlighted={true} width={new_width} />
        <div className="buttons-container">
            <button className="button-10" onClick={() => addImage(img_dir)}>Annotate</button>
        </div>
        {descs.map(desc => <p>{desc}<br /></p>)}
    </div>
}

function AnnotatedImage(image, map, addObject, new_width, objs, descs, img_dir, removeImage) {
    return <div className="image-container">
        {/* <img src={require(image)} className="center-image"/> */}
        <p>Image has been annotated</p>
        <ImageMapper src={require(image)} map={map} onClick={(area, index) => addObject(objs[index]['ObjPosInImgLeftToRight'])} width={new_width} />
        <div className="buttons-container">
            {/* <button className="button-10-2">Annotate</button> */}
            <button className="button-10" onClick={() => removeImage(img_dir)}>Unannotate</button>
        </div>
        {descs.map(desc => <p>{desc}<br /></p>)}
    </div>
}

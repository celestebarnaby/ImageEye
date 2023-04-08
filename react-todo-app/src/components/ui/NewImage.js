import React from 'react';
import ImageMapper from 'react-img-mapper';

export default function NewImage({ image, imgToEnvironment, annotatedImgs, addObject, addImage, imgDir }) {

    let img_dir = image ? "react-todo-app/src/components/ui" + image.slice(1) : null;
    let annotated = annotatedImgs.includes(img_dir)
    let annotations = annotated ? annotatedImgs[img_dir] : null;
    const new_width = 500;
    const cur_width = img_dir ? imgToEnvironment[img_dir]['dimensions'][0] : 0;
    const cur_height = img_dir ? imgToEnvironment[img_dir]['dimensions'][1] : 0;
    const new_height = cur_height * (new_width / cur_width);
    let env = img_dir ? imgToEnvironment[img_dir]['environment'] : [];
    let areas = Object.entries(env).map(([key, value]) => {
        const curX1 = value['Loc'][0];
        const curY1 = value['Loc'][1];
        const curX2 = value['Loc'][2];
        const curY2 = value['Loc'][3];
        return {
            shape: 'rect',
            coords: [
                curX1 * (new_width / cur_width),
                curY1 * (new_height / cur_height),
                curX2 * (new_width / cur_width),
                curY2 * (new_height / cur_height)
            ],
            id: key,
            preFillColor: ((annotated && annotations.includes(key)) ? "rgba(255, 255, 255, 0.5)" : undefined),
            // onClick: () => console.log('asdf')
        };
    });

    const map = {
        name: 'test',
        areas: areas
    };


    return (
        <div>
            {image && (
                annotated ? AnnotatedImage(image, map, addObject, new_width, addImage, img_dir) : UnannotatedImage(image, map, addObject, new_width, addImage, img_dir))}
        </div>
    );
}

function UnannotatedImage(image, map, addObject, new_width, addImage, img_dir) {
    return <div className="image-container">
        {/* <img src={require(image)} className="center-image"/> */}
        <ImageMapper src={require(image)} map={map} onClick={(area, index) => addObject(index)} toggleHighlighted={true} stayMultiHighlighted={true} width={new_width} />
        <div className="buttons-container">
            <button className="button-10" onClick={() => addImage(img_dir)}>Annotate</button>
        </div>
    </div>
}

function AnnotatedImage(image, map, addObject, new_width) {
    return <div className="image-container">
        {/* <img src={require(image)} className="center-image"/> */}
        <p>Image has been annotated</p>
        <ImageMapper src={require(image)} map={map} onClick={(area, index) => addObject(index)} stayMultiHighlighted={true} width={new_width} />
        <div className="buttons-container">
            <button className="button-10-2">Annotate</button>
        </div>
    </div>
}

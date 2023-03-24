import React from 'react';
import ImageMapper from 'react-img-mapper';

export default function NewImage({image, imgToEnvironment, addObject, addImage}) {

    let img_dir = image ? "react-todo-app/src/components/ui" + image.slice(1) : null;
    let env = img_dir ? imgToEnvironment[img_dir]['environment'] : [];
    let areas = Object.entries(env).map(([key, value]) => { 
        return {
            shape: 'rect',
            coords: value['Loc'],
            id: key,
            // onClick: () => console.log('asdf')
        };
    });

    const map = {
        name: 'test',
        areas: areas
    };


    return (
        <div >
            {image && (
            <div className="image-container">
            {/* <img src={require(image)} className="center-image"/> */}
                <ImageMapper src={require(image)} map={map} onClick={(area, index) => addObject(index)} className="center-image"/>
            <div className="buttons-container">
                <button className="button-10" onClick={() => addImage(img_dir)}>Mark as Positive</button>
                <button className="button-10">Mark as Negative</button>
            </div>
            </div>
            )}
        </div>
    );
}

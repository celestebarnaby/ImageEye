import React from 'react';

export default function NewImage({image, imgToEnvironment}) {

    let img_dir = image ? "react-todo-app/src/components/ui" + image.slice(1) : null;
    let env = img_dir ? imgToEnvironment[img_dir]['environment'] : [];
    let areas = Object.entries(env).map(([key, value]) => { 
        return {
            shape: 'rect',
            coords: value['Loc'],
            areaKeyName: key
        };
    });

    const map = {
        name: 'test',
        areas: areas
    };

    console.log('yoohoo');
    console.log(imgToEnvironment);
    console.log(env);
    console.log(areas);
    console.log(Object.entries(env));

    return (
        <div >
            {image && (
            <div className="image-container">
            {/* <img src={require(image)} className="center-image"/> */}
                <ImageMapper src={require(image)} map={map} toggleHighlighted={true} className="center-image"/>
            <div className="buttons-container">
                <button className="button-10">Mark as Positive</button>
                <button className="button-10">Mark as Negative</button>
            </div>
            </div>
            )}
        </div>
    );
}

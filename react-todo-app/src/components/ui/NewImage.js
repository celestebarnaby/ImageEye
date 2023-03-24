import React from 'react';
import ImageMapper from 'react-img-mapper';

export default function NewImage({image}) {

    const test = {
        name: 'test',
        areas: [
            {
                shape: 'rect',
                coords: [50, 50, 300, 300],
                strokeColor: "pink",
            }
        ]
    };

    return (
        <div >
            {image && (
            <div className="image-container">
            {/* <img src={require(image)} className="center-image"/> */}
                <ImageMapper src={require(image)} map={test} toggleHighlighted={true} className="center-image"/>
            <div className="buttons-container">
                <button className="button-10">Mark as Positive</button>
                <button className="button-10">Mark as Negative</button>
            </div>
            </div>
            )}
        </div>
    );
}

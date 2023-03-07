import React from 'react';

export default function NewImage({image}) {

    return (
        <div >
            {image && (
            <div className="image-container">
            <img src={require(image)} className="center-image"/>
            <div className="buttons-container">
                <button className="button-10">Mark as Positive</button>
                <button className="button-10">Mark as Negative</button>
            </div>
            </div>
            )}
        </div>
    );
}

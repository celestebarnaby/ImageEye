import React, { useState } from 'react';

function Sidebar({ allFiles, imgsToAnnotate, changeImage, annotatedImgs, handleTextChange, handleTextSubmit }) {
    const [selectedTab, setSelectedTab] = useState("tab1");

    return (
        <div className="sidebar">
            <textarea
                maxLength={100}
                rows={3}
                columns={20}
                onChange={handleTextChange}
            />
            <br />
            <button className="button-10" onClick={handleTextSubmit}>Submit</button>
            <div className="side-by-side">
                <button className="button-12" onClick={() => setSelectedTab("tab1")}>Images to Annotate</button>
                <button className="button-12" onClick={() => setSelectedTab("tab2")}>All Images</button>
                <button className="button-12" onClick={() => setSelectedTab("tab3")}>Annotated Images</button>
            </div>
            <div>
                {selectedTab === "tab1" ? AnnotationSuggestions(imgsToAnnotate, annotatedImgs, changeImage) : (selectedTab === "tab2" ? AllImages(allFiles, annotatedImgs, changeImage) : AnnotatedImages(allFiles, annotatedImgs, changeImage))}
            </div>
        </div>
    );
}

function AnnotationSuggestions(imgsToAnnotate, annotatedImgs, changeImage) {
    return <div>
        <ul>
            {imgsToAnnotate ?
                imgsToAnnotate.map(img => <li><img className={annotatedImgs.includes("image-search-gui/src/components/ui" + img.slice(1)) ? "small-img-grayed-out" : "small-img"} src={require(img)} key="{img}" onClick={() => changeImage(img)} /></li>)
                : <p>Enter text query to get annotation suggestions.</p>
            }
        </ul>
    </div>
}

function AllImages(allFiles, annotatedImgs, changeImage) {
    return <div>
        <ul>
            {allFiles ?
                allFiles.map(img => <li><img className={annotatedImgs.includes("image-search-gui/src/components/ui" + img.slice(1)) ? "small-img-grayed-out" : "small-img"} src={require(img)} key="{img}" onClick={() => changeImage(img)} /></li>)
                : <p>Enter text query to get annotation suggestions.</p>
            }
        </ul>
    </div>
}

function AnnotatedImages(allFiles, annotatedImgs, changeImage) {
    return <div>
        <ul>
            {allFiles ?
                allFiles.filter(img => annotatedImgs.includes("image-search-gui/src/components/ui" + img.slice(1))).map(img => <li><img className={"small-img"} src={require(img)} key="{img}" onClick={() => changeImage(img)} /></li>)
                : <p>Annotated images will be listed here.</p>
            }
        </ul>
    </div>
}

export default Sidebar;
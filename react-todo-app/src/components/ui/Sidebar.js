import React, { useState } from 'react';
// import ResizableTextarea from 'react-resizable-textarea';



function Sidebar({ allFiles, imgsToAnnotate, changeImage, annotatedImgs, handleTextChange, handleTextSubmit }) {
    const [selectedTab, setSelectedTab] = useState("tab1");

    // const handleTabClick = (tab) => {
    //     setSelectedTab(tab);
    // };


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
                {/* <div>
            <h4>Likely a Match</h4>
            <ul>
                {imgs.map(img => <li><img className="small-img" src={require(img)} key="{img}" onClick={() => changeImage(img)}/></li> )}
            </ul>
        </div> */}
                {selectedTab == "tab1" ? AnnotationSuggestions(imgsToAnnotate, annotatedImgs, changeImage) : (selectedTab == "tab2" ? AllImages(allFiles, annotatedImgs, changeImage) : AnnotatedImages(allFiles, annotatedImgs, changeImage))}
            </div>
        </div>
    );
}

function AnnotationSuggestions(imgsToAnnotate, annotatedImgs, changeImage) {
    return <div>
        {/* <h3>Images to Annotate</h3> */}
        <ul>
            {imgsToAnnotate ?
                imgsToAnnotate.map(img => <li><img className={annotatedImgs.includes("react-todo-app/src/components/ui" + img.slice(1)) ? "small-img-grayed-out" : "small-img"} src={require(img)} key="{img}" onClick={() => changeImage(img)} /></li>)
                : <p>Enter text query to get annotation suggestions.</p>
            }
        </ul>
    </div>
}

function AllImages(allFiles, annotatedImgs, changeImage) {
    console.log('hi');
    console.log(allFiles);
    return <div>
        {/* <h3>All Images</h3> */}
        <ul>
            {allFiles ?
                allFiles.map(img => <li><img className={annotatedImgs.includes("react-todo-app/src/components/ui" + img.slice(1)) ? "small-img-grayed-out" : "small-img"} src={require(img)} key="{img}" onClick={() => changeImage(img)} /></li>)
                : <p>Enter text query to get annotation suggestions.</p>
            }
        </ul>
    </div>
}

function AnnotatedImages(allFiles, annotatedImgs, changeImage) {
    return <div>
        {/* <h3>All Images</h3> */}
        <ul>
            {allFiles ?
                allFiles.filter(img => annotatedImgs.includes("react-todo-app/src/components/ui" + img.slice(1))).map(img => <li><img className={"small-img"} src={require(img)} key="{img}" onClick={() => changeImage(img)} /></li>)
                : <p>Annotated images will be listed here.</p>
            }
        </ul>
    </div>
}

export default Sidebar;
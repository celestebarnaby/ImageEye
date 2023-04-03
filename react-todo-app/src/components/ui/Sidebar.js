import React, { useState } from 'react';
// import ResizableTextarea from 'react-resizable-textarea';



function Sidebar({files, changeImage, annotatedImgs, handleTextChange, handleTextSubmit}) {
    console.log('sidebar');
    console.log(files);
    const imgs = files ? files : ['./images/1.jpg', './images/2.jpg', './images/3.jpg'];
    // const imgs = ['./images/wedding/wedding1.jpg', './images/wedding/wedding2.jpg', './images/wedding/3.jpg'];
    console.log('sidebar');
    console.log(imgs);
    console.log(annotatedImgs);
    console.log("react-todo-app/src/components/ui" + imgs[0].slice(1));
    console.log(annotatedImgs.includes("react-todo-app/src/components/ui" + imgs[0].slice(1)));
    // const imgs = ['./1.jpg', './2.jpg', './3.jpg'];
    // const imgs = files.map(file => file.name);

  return (
    <div className="sidebar">
        <textarea 
            maxLength={100} 
            rows={3}
            columns={20}  
            onChange={handleTextChange}
        />
        <br/>
        <button className="button-10" onClick={handleTextSubmit}>Submit</button>
      <h3>Images to Annotate</h3>
      <div>
        {/* <div>
            <h4>Likely a Match</h4>
            <ul>
                {imgs.map(img => <li><img className="small-img" src={require(img)} key="{img}" onClick={() => changeImage(img)}/></li> )}
            </ul>
        </div> */}
        <div>
            {/* <h4>Likely Not a Match</h4> */}
            <ul>
                {imgs.map(img => <li><img className={annotatedImgs.includes("react-todo-app/src/components/ui" + img.slice(1)) ? "small-img-grayed-out" : "small-img"} src={require(img)} key="{img}" onClick={() => changeImage(img)}/></li> )}
            </ul>
        </div>
        </div>
    </div>
  );
}

export default Sidebar;
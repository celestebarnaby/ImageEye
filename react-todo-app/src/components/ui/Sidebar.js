import React, { useState } from 'react';
// import ResizableTextarea from 'react-resizable-textarea';



function Sidebar({files, changeImage}) {
    console.log('sidebar');
    console.log(files);
    const imgs = files ? files : ['./images/1.jpg', './images/2.jpg', './images/3.jpg'];
    // const imgs = ['./images/wedding/wedding1.jpg', './images/wedding/wedding2.jpg', './images/wedding/3.jpg'];
    console.log('sidebar');
    console.log(imgs);
    // const imgs = ['./1.jpg', './2.jpg', './3.jpg'];
    // const imgs = files.map(file => file.name);

  return (
    <div className="sidebar">
      <form>
        {/* <input type="text" /> */}
        <textarea 
            maxLength={100} 
            rows={3}
            columns={20}  
        />
        <br/>
        <button className="button-10" type="submit">Submit</button>
      </form>
      <h3>Images to Annotate</h3>
      <div className="side-by-side">
        <div>
            <h4>Likely a Match</h4>
            <ul>
                {imgs.map(img => <li><img className="small-img" src={require(img)} key="{img}" onClick={() => changeImage(img)}/></li> )}
            </ul>
        </div>
        <div>
            <h4>Likely Not a Match</h4>
            <ul>
                {imgs.map(img => <li><img className="small-img" src={require(img)} key="{img}" onClick={() => changeImage(img)}/></li> )}
            </ul>
        </div>
        </div>
    </div>
  );
}

export default Sidebar;
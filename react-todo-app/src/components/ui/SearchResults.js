import React, { useState } from 'react';

function SearchResults({files, changeImage}) {
    const imgs = files ? Array.from(files).map(file => './' + file.name) : ['./1.jpg', './2.jpg', './3.jpg'];

  return (
    <div className="search-results">
        <h3>Search Results</h3>
        <ul>
        {imgs.map(img => <li><img className="small-img" key="{img}" onClick={() => changeImage(img)} src={require(img)}/></li> )}
        </ul>
    </div>
  );
}

export default SearchResults;
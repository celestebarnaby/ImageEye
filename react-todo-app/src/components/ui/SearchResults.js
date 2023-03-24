import React, { useState } from 'react';

function SearchResults({files, changeImage, result}) {
    const imgs = files ? files : ['./images/1.jpg', './images/2.jpg', './images/3.jpg'];

  return (
    <div className="search-results">
        <h3>Search Results</h3>
        {
          result && (<p>{result}</p>)
        }
        <ul>
        {imgs.map(img => <li><img className="small-img" key="{img}" onClick={() => changeImage(img)} src={require(img)}/></li> )}
        </ul>
    </div>
  );
}

export default SearchResults;
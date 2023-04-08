import React, { useState } from 'react';

function SearchResults({ files, changeImage, result }) {

  return (
    <div className="search-results">
      <h3>Search Results</h3>
      <ul>
        {
          result && (<p>{result}</p>)
        }
        {files ?
          files.map(img => <li><img className="small-img" key="{img}" onClick={() => changeImage(img)} src={require(img)} /></li>)
          : <p>Enter text query to generate search results.</p>
        }
      </ul>
    </div>
  );
}

export default SearchResults;
import React from 'react';

function MenuBar({ updateResults }) {
  return (
    <div className="bottom-menu-bar">
      <button className="button-10" onClick={() => updateResults()}>Update Results</button>
    </div>
  );
}

export default MenuBar;
import React, { useState } from 'react';
import Sidebar from '../ui/Sidebar';
import NewImage from '../ui/NewImage';
import SearchResults from '../ui/SearchResults';
import MenuBar from '../ui/MenuBar';
import { ReactDialogBox } from 'react-js-dialog-box'
import 'react-js-dialog-box/dist/index.css'

function App() {
  const [message, setMessage] = useState("");
  const [isOpen, setIsOpen] = useState(true);
  const [files, setFiles] = useState(null);
  const [sidebarFiles, setSidebarFiles] = useState(null);
  const [searchResults, setSearchResults] = useState(null);
  const [mainImage, setMainImage] = useState(null);
  const [objectList, setObjectList] = useState([]);
  const [annotatedImages, setAnnotatedImages] = useState({});
  const [result, setResult] = useState(null);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  let closeBox = () => {
    setIsOpen(false);
  };

  let closeError = () => {
    setErrorMessage('');
  }

  let handleTextChange = (event) => {
    setInputText(event.target.value);
  }

  let removeImage = (img_dir) => {
    delete annotatedImages[img_dir]
    setAnnotatedImages({ ...annotatedImages });
  }

  let handleTextSubmit = () => {
    setIsLoading(true);
    fetch('/textQuery', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(inputText)
    })
      .then(response => response.json())
      .then(data => {
        setSearchResults(data.searchResults);
        setSidebarFiles(data.sidebarFiles);
        setIsLoading(false);
        setMainImage(data.sidebarFiles[0]);
      })
  }

  let handleChange = (img_dir) => {
    setIsOpen(false);
    setIsLoading(true);
    fetch('/loadFiles', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(img_dir)
    })
      .then(response => response.json())
      .then(data => {
        setFiles(data.files);
        setSidebarFiles(data.sidebarFiles);
        setMessage(data.message);
        setIsLoading(false);
      })
  };

  let changeImage = (image) => {
    setMainImage(image);
    setObjectList([]);
  };

  let addObject = (index) => {
    if (objectList.includes(index)) {
      const other_index = objectList.indexOf(index);
      objectList.splice(other_index, 1); // 2nd parameter means remove one item only
    }
    else {
      objectList.push(index);
    }
    setObjectList([...objectList]);
  }

  let addImage = (image) => {
    annotatedImages[image] = objectList;
    setAnnotatedImages({ ...annotatedImages });
    setObjectList([]);
  }

  function getAnnotationDescriptions(objs, annotations, annotated) {
    let l = annotated ? annotations : objectList;
    return l.map(i => objs[i]["Description"]);
  }


  let updateResults = () => {
    const vals = Object.values(annotatedImages);
    var hasPosExample = vals.some(val => val.length > 0);
    if (hasPosExample) {
      setIsLoading(true);
      fetch('/synthesize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(annotatedImages)
      })
        .then(response => response.json())
        .then(data => {
          console.log('Success:', data);
          if (data.program === null) {
            setErrorMessage("Synthesizer timed out");
            setIsLoading(false);
          } else {
            setResult(data.program);
            setSearchResults(data.search_results);
            setSidebarFiles(data.recs);
            setIsLoading(false);
          }
        })
        .catch((error) => {
          console.error('Error:', error);
        });
    } else {
      setErrorMessage("You need at least one positive example!");
    }

  }

  return (
    <div>
      <Sidebar
        imgsToAnnotate={sidebarFiles}
        allFiles={files}
        changeImage={changeImage}
        handleTextChange={handleTextChange}
        handleTextSubmit={handleTextSubmit}
        annotatedImgs={Object.keys(annotatedImages)}
      />
      <NewImage
        image={mainImage}
        annotatedImgs={annotatedImages}
        imgToEnvironment={message}
        addObject={addObject}
        addImage={addImage}
        removeImage={removeImage}
        getAnnotationDescriptions={getAnnotationDescriptions}
      />
      <SearchResults files={searchResults} changeImage={changeImage} result={result} />
      <MenuBar updateResults={updateResults} />

      {isOpen && (
        <ReactDialogBox
          closeBox={closeBox}
          modalWidth='60%'
          headerBackgroundColor='red'
          headerTextColor='white'
          headerHeight='65'
          closeButtonColor='white'
          bodyBackgroundColor='white'
          bodyTextColor='black'
          bodyHeight='200px'
          headerText='Title'
        >
          <div>
            <h1>Select Image Directory</h1>
            <div className="side-by-side">
              <button className="button-12" onClick={() => handleChange('receipts')}>Receipts</button>
              <button className="button-12" onClick={() => handleChange('objects')}>Objects</button>
              <button className="button-12" onClick={() => handleChange('wedding')}>Wedding</button>
            </div>
          </div>
        </ReactDialogBox>
      )}
      {isLoading && (
        <ReactDialogBox
          modalWidth='60%'
          headerTextColor='white'
          headerHeight='65'
          closeButtonColor='white'
          bodyBackgroundColor='white'
          bodyTextColor='black'
          bodyHeight='200px'
          headerText='Title'
        >
          <div>
            <p>Loading...</p>
          </div>
        </ReactDialogBox>
      )}
      {(errorMessage !== "") && (
        <ReactDialogBox
          closeBox={closeError}
          modalWidth='60%'
          headerBackgroundColor='red'
          headerTextColor='white'
          headerHeight='65'
          closeButtonColor='white'
          bodyBackgroundColor='white'
          bodyTextColor='black'
          bodyHeight='200px'
          headerText='Title'
        >
          <div>
            <p>{errorMessage}</p>
          </div>
        </ReactDialogBox>
      )

      }
    </div>
  );
}

export default App;

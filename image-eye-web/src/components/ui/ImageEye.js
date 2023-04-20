import React, { useState } from 'react';
import Sidebar from './Sidebar';
import NewImage from './NewImage';
import SearchResults from './SearchResults';


import Box from '@mui/material/Box';


export function ImageEye({ data }) {

  const [message, setMessage] = useState(data.message);
  const [files, setFiles] = useState(data.files);
  const [sidebarFiles, setSidebarFiles] = useState(data.sidebarFiles);
  const [searchResults, setSearchResults] = useState(null);
  const [mainImage, setMainImage] = useState(null);
  const [objectList, setObjectList] = useState([]);
  const [annotatedImages, setAnnotatedImages] = useState({});
  const [result, setResult] = useState(null);
  const [inputText, setInputText] = useState("");

  // setFiles(data.files);
  //       setSidebarFiles(data.sidebarFiles);
  //       setMessage(data.message);

  let handleTextChange = (event) => {
    setInputText(event.target.value);
  }

  let removeImage = (img_dir) => {
    delete annotatedImages[img_dir]
    setAnnotatedImages({ ...annotatedImages });
  }

  let handleTextSubmit = () => {
    setIsLoading(true);
    fetch('http://127.0.0.1:5000/textQuery', {
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
      fetch('http://127.0.0.1:5000/synthesize', {
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
    <Box sx={{display: "flex", flexDirection: "row", height: "100%"}}>
      <Sidebar
        imgsToAnnotate={sidebarFiles}
        allFiles={files}
        changeImage={changeImage}
        handleTextChange={handleTextChange}
        handleTextSubmit={handleTextSubmit}
        annotatedImgs={Object.keys(annotatedImages)}
        updateResults={updateResults}
      />
      <Box sx={{flex: 1}}>
        <NewImage
          image={mainImage}
          annotatedImgs={annotatedImages}
          imgToEnvironment={message}
          addObject={addObject}
          addImage={addImage}
          removeImage={removeImage}
          getAnnotationDescriptions={getAnnotationDescriptions}
        />
      </Box>
      <SearchResults files={searchResults} changeImage={changeImage} result={result} />

      
    </Box>
  );
}
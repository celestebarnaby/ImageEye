import React, { useState } from 'react';
import AppBar from '@mui/material/AppBar';
import Button from '@mui/material/Button';
import CameraIcon from '@mui/icons-material/PhotoCamera';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Link from '@mui/material/Link';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { ImageEye } from './components/ui/ImageEye';
import DialogTitle from '@mui/material/DialogTitle';
import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';
import { SubmittedResults } from './components/ui/SubmittedResults';


function Copyright() {
  return (
    <Typography variant="body2" color="text.secondary" align="center">
      {'Copyright © '}
      <Link color="inherit" href="https://mui.com/">
        Your Website
      </Link>{' '}
      {new Date().getFullYear()}
      {'.'}
    </Typography>
  );
}

const theme = createTheme();

export default function App() {

  // const [dataset, setDataset] = useState(null);

  const [isOpen, setIsOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [inputText, setInputText] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [sidebarFiles, setSidebarFiles] = useState([]);
  const [mainImage, setMainImage] = useState(null);
  const [objectList, setObjectList] = useState([]);
  const [annotatedImages, setAnnotatedImages] = useState({});
  const [result, setResult] = useState(null);
  const [message, setMessage] = useState({});
  const [files, setFiles] = useState([]);
  const [tentativeSubmit, setTentativeSubmit] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [manuallyAdded, setManuallyAdded] = useState(new Set());
  const [manuallyRemoved, setManuallyRemoved] = useState(new Set());

  let closeError = () => {
    setErrorMessage('');
  }

  let closeBox = () => {
    setIsOpen(false);
  };

  let changeImage = (image) => {
    setMainImage(image);
    setObjectList([]);
  };

  let handleTextChange = (event) => {
    setInputText(event.target.value);
  }

  let addObject = (index, remove_if_already_present) => {
    if (objectList.includes(index)) {
      if (remove_if_already_present) {
        const other_index = objectList.indexOf(index);
        objectList.splice(other_index, 1); // 2nd parameter means remove one item only
      }
    }
    else {
      objectList.push(index);
    }
    setObjectList([...objectList]);
  }

  let addObjectsByName = (name, objs) => {
    if (name != "Face" && name != "Text") {
      let new_indices = objs.filter(obj => obj['Name'] == name).map(obj => obj['ObjPosInImgLeftToRight']);
      let already_added = objs.filter(obj => obj['Name'] == name && objectList.includes(obj['ObjPosInImgLeftToRight']));
      let remove_if_already_present = (new_indices.length == already_added.length)
      new_indices.forEach(index => addObject(index, remove_if_already_present));
    }
    else {
      let new_indices = objs.filter(obj => obj['Type'] == name).map(obj => obj['ObjPosInImgLeftToRight']);
      let already_added = objs.filter(obj => obj['Type'] == name && objectList.includes(obj['ObjPosInImgLeftToRight']));
      let remove_if_already_present = (new_indices.length == already_added.length)
      new_indices.forEach(index => addObject(index, remove_if_already_present));
    }
    setObjectList([...objectList]);
  }

  let addImage = (image) => {
    annotatedImages[image] = objectList;
    setAnnotatedImages({ ...annotatedImages });
    setObjectList([]);
  }

  let removeImage = (img_dir) => {
    delete annotatedImages[img_dir]
    setAnnotatedImages({ ...annotatedImages });
  }

  let handleSearchResults = (img_dir) => {
    if (searchResults.includes(img_dir)) {
      const index = searchResults.indexOf(img_dir);
      searchResults.splice(index, 1);
      manuallyRemoved.add(img_dir)
    } else {
      searchResults.push(img_dir);
      manuallyAdded.add(img_dir)
    }
    setSearchResults([...searchResults]);
    setManuallyAdded(manuallyAdded);
    setManuallyRemoved(manuallyRemoved);
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
        setFiles(data.files);
        // setDataset([]);
        // setSidebarFiles(data.sidebarFiles);
        setIsLoading(false);
        setMainImage(data.sidebarFiles[0]);
      })
  }

  let handleChange = (img_dir) => {
    setIsOpen(false);
    setIsLoading(true);
    fetch('http://127.0.0.1:5000/loadFiles', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(img_dir)
    })
      .then(response => response.json())
      .then(data => {

        setFiles(data.files);
        setMessage(data.message);
        setIsLoading(false);
      })
  };

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
            setManuallyAdded(new Set());
            setManuallyRemoved(new Set());
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

  let submitResults = () => {
    setTentativeSubmit(true);
  }

  let submitResults2 = (val) => {
    setSubmitted(val);
    setTentativeSubmit(false);
    if (val) {
      fetch('http://127.0.0.1:5000/submitResults', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        // body: JSON.stringify(searchResults)
        body: JSON.stringify({ results: searchResults, manually_added: Array.from(manuallyAdded), manually_removed: Array.from(manuallyRemoved) })
      })
    }
  }


  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: "block" }}>
        <AppBar position="relative">
          <Toolbar>
            <CameraIcon sx={{ mr: 2 }} />
            <Typography variant="h6" color="inherit" noWrap>
              Tool B
            </Typography>
            {/* <Button variant="outlined" sx={{ color: "white" }}>Upload Images</Button> */}
          </Toolbar>
        </AppBar>
        <Box
          sx={{
            display: "block",
            height: "calc(100vh - 64px)"
          }}
        >
          {!submitted ? <ImageEye
            files={files}
            message={message}
            updateResults={updateResults}
            handleTextChange={handleTextChange}
            handleTextSubmit={handleTextSubmit}
            searchResults={searchResults}
            sidebarFiles={sidebarFiles}
            mainImage={mainImage}
            changeImage={changeImage}
            addObject={addObject}
            addObjectsByName={addObjectsByName}
            addImage={addImage}
            removeImage={removeImage}
            objectList={objectList}
            annotatedImages={annotatedImages}
            result={result}
            submitResults={submitResults}
            handleSearchResults={handleSearchResults}
          /> : <SubmittedResults searchResults={searchResults} />}
        </Box>
      </Box>
      <Dialog open={isOpen}>
        <DialogTitle>Select Task</DialogTitle>
        <DialogContent>
          <div className="side-by-side">
            <button className="button-12" onClick={() => handleChange(1)}>1</button>
            <button className="button-12" onClick={() => handleChange(2)}>2</button>
            <button className="button-12" onClick={() => handleChange(3)}>3</button>
            <button className="button-12" onClick={() => handleChange(4)}>4</button>
            <button className="button-12" onClick={() => handleChange(5)}>5</button>
            <button className="button-12" onClick={() => handleChange(6)}>6</button>
          </div>
        </DialogContent>
      </Dialog>
      <Dialog open={isLoading}>
        <DialogContent>
          <p>Loading...</p>
        </DialogContent>
      </Dialog>
      <Dialog open={tentativeSubmit}>
        <DialogTitle>Are you sure you want to submit your results?</DialogTitle>
        <DialogContent>
          <div className="side-by-side">
            <button className="button-12" onClick={() => submitResults2(true)}>Yes</button>
            <button className="button-12" onClick={() => submitResults2(false)}>No</button>
          </div>
        </DialogContent>
      </Dialog>
    </ThemeProvider>
  );
}
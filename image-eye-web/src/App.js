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
import IconButton from '@mui/material/IconButton';
import CloseIcon from '@mui/icons-material/Close';


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
  const [exampleImages, setExampleImages] = useState({});
  const [result, setResult] = useState(null);
  const [message, setMessage] = useState({});
  const [files, setFiles] = useState([]);
  const [tentativeSubmit, setTentativeSubmit] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [savedImages, setSavedImages] = useState([]);
  const [selectedObject, setSelectedObject] = useState(null);
  const [robotText, setRobotText] = useState("Enter text query and add example images to begin search.")
  const [robotText2, setRobotText2] = useState("");
  const [manuallyAdded, setManuallyAdded] = useState([]);
  const [manuallyRemoved, setManuallyRemoved] = useState([]);

  let closeError = () => {
    setErrorMessage('');
  }

  let closeBox = () => {
    setIsOpen(false);
  };

  let changeImage = (image) => {
    setMainImage(image);
    setSelectedObject(null);
    // setObjectList([]);
  };

  let handleTextChange = (event) => {
    setInputText(event.target.value);
  }

  let selectObject = (index) => {
    setSelectedObject(index);
  }

  let deselectObject = () => {
    setSelectedObject(null);
  }

  let addImage = (image, val) => {
    exampleImages[image] = val;
    setExampleImages({ ...exampleImages });
  }

  let removeImage = (img_dir) => {
    delete exampleImages[img_dir]
    setExampleImages({ ...exampleImages });
  }

  let addToSavedImages = (images) => {
    images.forEach(image => handleSavedImages(image, false, false));
  }

  let handleSavedImages = (img_dir, remove_if_present, manual) => {
    if (savedImages.includes(img_dir)) {
      if (remove_if_present) {
        const index = savedImages.indexOf(img_dir);
        savedImages.splice(index, 1);
      }
      if (manual) {
        manuallyRemoved.push(img_dir);
      }
    } else {
      savedImages.push(img_dir);
      if (manual) {
        manuallyAdded.push(img_dir);
      }
    }
    setSavedImages([...savedImages]);
  }


  let handleTextSubmit = () => {
    setIsLoading(true);
    var body = { text_query: inputText, examples: exampleImages }
    fetch('http://127.0.0.1:5001/textQuery', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      // body: JSON.stringify(inputText)
      body: JSON.stringify(body)
    })
      .then(response => response.json())
      .then(data => {
        setResult(data.program);
        setSearchResults(data.search_results);
        setIsLoading(false);
        setRobotText(data.robot_text);
        setRobotText2(data.robot_text2);
      })
  }

  let handleChange = (img_dir) => {
    setIsOpen(false);
    setIsLoading(true);
    fetch('http://127.0.0.1:5001/loadFiles', {
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
    const vals = Object.values(exampleImages);
    var hasPosExample = vals.some(val => val.length > 0);
    if (hasPosExample) {
      setIsLoading(true);
      fetch('http://127.0.0.1:5001/synthesize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(exampleImages)
      })
        .then(response => response.json())
        .then(data => {
          console.log('Success:', data);
          if (data.program === null) {
            setErrorMessage("Search timed out");
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

  let submitSavedImages = () => {
    setTentativeSubmit(true);
  }

  let submitSavedImages2 = (val) => {
    setSubmitted(val);
    setTentativeSubmit(false);
    if (val) {
      fetch('http://127.0.0.1:5001/submitResults', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        // body: JSON.stringify(searchResults)
        body: JSON.stringify({ results: searchResults, manually_added: manuallyAdded, manually_removed: manuallyRemoved })
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
            selectObject={selectObject}
            // addObjectsByName={addObjectsByName}
            addImage={addImage}
            removeImage={removeImage}
            selectedObject={selectedObject}
            exampleImages={exampleImages}
            result={result}
            submitSavedImages={submitSavedImages}
            savedImages={savedImages}
            handleSavedImages={handleSavedImages}
            addToSavedImages={addToSavedImages}
            robotText={robotText}
            robotText2={robotText2}
            setSavedImages={setSavedImages}
          /> : <SubmittedResults searchResults={searchResults} />}
        </Box>
      </Box>
      <Dialog open={isOpen}>
        <DialogTitle>Select Task</DialogTitle>
        <DialogContent>
          <div className="side-by-side">
            <button className="button-12" onClick={() => handleChange(0)}>Practice Task</button>
            <button className="button-12" onClick={() => handleChange(1)}>1</button>
            <button className="button-12" onClick={() => handleChange(2)}>2</button>
            <button className="button-12" onClick={() => handleChange(3)}>3</button>
            <button className="button-12" onClick={() => handleChange(4)}>4</button>
            <button className="button-12" onClick={() => handleChange(5)}>5</button>
            <button className="button-12" onClick={() => handleChange(6)}>6</button>
          </div>
        </DialogContent>
      </Dialog>
      {/* <Dialog open={isOpen}>
        <DialogTitle>Select Dataset</DialogTitle>
        <DialogContent>
          <div className="side-by-side">
            <button className="button-12" onClick={() => handleChange(0)}>Objects</button>
            <button className="button-12" onClick={() => handleChange(1)}>Concert</button>
            <button className="button-12" onClick={() => handleChange(3)}>Wedding</button>
          </div>
        </DialogContent>
      </Dialog> */}
      <Dialog open={errorMessage}>
        <DialogTitle>
          <IconButton
            aria-label="close"
            onClick={() => setErrorMessage('')}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
              color: (theme) => theme.palette.grey[500],
            }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {errorMessage}
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
            <button className="button-12" onClick={() => submitSavedImages2(true)}>Yes</button>
            <button className="button-12" onClick={() => submitSavedImages2(false)}>No</button>
          </div>
        </DialogContent>
      </Dialog>
    </ThemeProvider>
  );
}
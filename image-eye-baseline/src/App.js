import React, { useState } from 'react';
import AppBar from '@mui/material/AppBar';
import Button from '@mui/material/Button';
import CameraIcon from '@mui/icons-material/PhotoCamera';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Link from '@mui/material/Link';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { ImageEye } from './components/ui/ImageEye';
import { SubmittedResults } from './components/ui/SubmittedResults';
import DialogTitle from '@mui/material/DialogTitle';
import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';


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
  const [message, setMessage] = useState({});
  const [files, setFiles] = useState([]);
  const [tentativeSubmit, setTentativeSubmit] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [savedImages, setSavedImages] = useState([]);


  let closeError = () => {
    setErrorMessage('');
  }

  let closeBox = () => {
    setIsOpen(false);
  };

  let changeImage = (image) => {
    setMainImage(image);
  };

  let handleTextChange = (event) => {
    setInputText(event.target.value);
  }

  let submitSavedImages = () => {
    setTentativeSubmit(true);
  }

  let submitSavedImages2 = (val) => {
    setSubmitted(val);
    setTentativeSubmit(false);
    if (val) {
      fetch('http://127.0.0.1:5000/submitResults', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        // body: JSON.stringify(searchResults)
        body: JSON.stringify({ results: savedImages })
      })
    }
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
        setSearchResults(data.search_results);
        // setManuallyAdded(new Set());
        // setManuallyRemoved(new Set());
        setIsLoading(false);
      })
  }

  let addToSavedImages = (images) => {
    images.forEach(image => handleSavedImages(image, false));
  }

  let handleSavedImages = (img_dir, remove_if_present) => {
    if (savedImages.includes(img_dir)) {
      if (remove_if_present) {
        const index = savedImages.indexOf(img_dir);
        savedImages.splice(index, 1);
      }
      // manuallyRemoved.add(img_dir)
    } else {
      savedImages.push(img_dir);
      // manuallyAdded.add(img_dir)
    }
    setSavedImages([...savedImages]);
    // setManuallyAdded(manuallyAdded);
    // setManuallyRemoved(manuallyRemoved);
  }


  let handleImageSubmit = (image) => {
    setIsLoading(true);
    fetch('http://127.0.0.1:5000/imageQuery', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(image)
    })
      .then(response => response.json())
      .then(data => {
        setSearchResults(data.search_results);
        // setManuallyAdded(new Set());
        // setManuallyRemoved(new Set());
        setIsLoading(false);
      })
  }


  let handleChange = (task_num) => {
    setIsOpen(false);
    setIsLoading(true);
    fetch('http://127.0.0.1:5000/loadFiles', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(task_num)
    })
      .then(response => response.json())
      .then(data => {

        setFiles(data.files);
        setMessage(data.message);
        setIsLoading(false);
      })
  };


  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: "block" }}>
        <AppBar position="relative">
          <Toolbar sx={{ backgroundColor: "#D27519" }}>
            <CameraIcon sx={{ mr: 2 }} />
            <Typography variant="h6" color="inherit" noWrap>
              Tool A
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
            handleTextChange={handleTextChange}
            handleTextSubmit={handleTextSubmit}
            handleImageSubmit={handleImageSubmit}
            handleSavedImages={handleSavedImages}
            searchResults={searchResults}
            sidebarFiles={sidebarFiles}
            mainImage={mainImage}
            changeImage={changeImage}
            submitSavedImages={submitSavedImages}
            savedImages={savedImages}
            addToSavedImages={addToSavedImages}
          /> : <SubmittedResults searchResults={savedImages} />}
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
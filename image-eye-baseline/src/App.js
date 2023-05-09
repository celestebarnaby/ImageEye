import React, { useState } from 'react';
import AppBar from '@mui/material/AppBar';
import Button from '@mui/material/Button';
import CameraIcon from '@mui/icons-material/PhotoCamera';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import CssBaseline from '@mui/material/CssBaseline';
import Grid from '@mui/material/Grid';
import Stack from '@mui/material/Stack';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Link from '@mui/material/Link';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { ImageEye } from './components/ui/ImageEye';
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
  const [searchResults, setSearchResults] = useState(null);
  const [sidebarFiles, setSidebarFiles] = useState([]);
  const [mainImage, setMainImage] = useState(null);
  const [objectList, setObjectList] = useState([]);
  const [annotatedImages, setAnnotatedImages] = useState({});
  const [result, setResult] = useState(null);
  const [message, setMessage] = useState({});
  const [files, setFiles] = useState([]);


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
        setIsLoading(false);
      })
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
        setIsLoading(false);
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
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: "block" }}>
        <AppBar position="relative">
          <Toolbar>
            <CameraIcon sx={{ mr: 2 }} />
            <Typography variant="h6" color="inherit" noWrap>
              Image Eye
            </Typography>
            <Button variant="outlined" sx={{ color: "white" }}>Upload Images</Button>
          </Toolbar>
        </AppBar>
        <Box
          sx={{
            display: "block",
            height: "calc(100vh - 64px)"
          }}
        >
          {files ? <ImageEye
            files={files}
            message={message}
            updateResults={updateResults}
            handleTextChange={handleTextChange}
            handleTextSubmit={handleTextSubmit}
            handleImageSubmit={handleImageSubmit}
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
          /> : <Typography sx={{ margin: "auto" }}>Select a dataset to get started.</Typography>}
        </Box>
      </Box>
      <Dialog onClose={closeBox} open={isOpen || isLoading}>
        <DialogTitle>Select Image Directory</DialogTitle>
        <DialogContent>
          {isLoading ? <p>Loading...</p> : <div>
            <div className="side-by-side">
              <button className="button-12" onClick={() => handleChange('receipts')}>Receipts</button>
              <button className="button-12" onClick={() => handleChange('objects')}>Objects</button>
              <button className="button-12" onClick={() => handleChange('wedding2')}>Wedding</button>
              <button className="button-12" onClick={() => handleChange('concert')}>Concert</button>
            </div>
          </div>}
        </DialogContent>
      </Dialog>
    </ThemeProvider>
  );
}
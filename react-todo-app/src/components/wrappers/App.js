import React, { Component, useState, useEffect } from 'react';
import Sidebar from '../ui/Sidebar';
import NewImage from '../ui/NewImage';
import SearchResults from '../ui/SearchResults';
import MenuBar from '../ui/MenuBar';
import { ReactDialogBox } from 'react-js-dialog-box'
import 'react-js-dialog-box/dist/index.css'
import FileUploadButton from '../ui/FileUploadButton';

function App() {
  // usestate for setting a javascript
  // object for storing and using data
  const [message, setMessage] = useState("");
  const [isOpen, setIsOpen] = useState(true);
  const [files, setFiles] = useState(null);
  const [sidebarFiles, setSidebarFiles] = useState(null);
  const [searchResults, setSearchResults] = useState(null);
  const [mainImage, setMainImage] = useState(null);
  const objectList = [];
  const [annotatedImages2, setAnnotatedImages2] = useState({});
  const [result, setResult] = useState(null);
  const [imgDir, setImgDir] = useState("");
  const [inputText, setInputText] = useState("hi");
  const [isLoading, setIsLoading] = useState(false);
  const [stupid, setStupid] = useState(0);
  const [errorMessage, setErrorMessage] = useState('');

  // Using useEffect for single rendering
  // useEffect(() => {
  //     // Using fetch to fetch the api from 
  //     // flask server it will be redirected to proxy
  //     fetch("/data").then((res) => {
  //         res.json().then((data) => {
  //             // Setting a data from api
  //             setMessage(data.message);
  //         });
  //       });
  // }, []);

  let openBox = () => {
    setIsOpen(true);
  };

  let closeBox = () => {
    setIsOpen(false);
  };

  let closeError = () => {
    setErrorMessage('');
  }

  let handleTextChange = (event) => {
    setInputText(event.target.value);
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
    // setSelectedFiles(event.target.files);
    setIsOpen(false);
    setImgDir(img_dir);
    // setFiles(Array.from(event.target.files).map(file => './images/' + file.name))
    // setFiles(event.target.files);
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
        // setMainImage(data.files[0]);
      })
  };

  let changeImage = (image) => {
    setMainImage(image);
  };

  let addObject = (index) => {
    if (objectList.includes(index)) {
      const index = objectList.indexOf(index);
      objectList.splice(index, 1); // 2nd parameter means remove one item only
    }
    else {
      objectList.push(index);
    }
  }

  let addImage = (image) => {
    annotatedImages2[image] = objectList;
    console.log("annotated image added");
    console.log(annotatedImages2);
    setAnnotatedImages2(annotatedImages2);
    setStupid(stupid + 1);
  }

  let updateResults = () => {
    console.log('hi');
    console.log(annotatedImages2);
    const vals = Object.values(annotatedImages2);
    var hasPosExample = vals.some(val => val.length > 0);
    if (hasPosExample) {
      setIsLoading(true);
      fetch('/synthesize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(annotatedImages2)
      })
        .then(response => response.json())
        .then(data => {
          console.log('Success:', data);
          if (data.program === null) {
            setErrorMessage("Synthesizer timed out");
            setIsLoading(false);
          } else {
            setResult(data.program);
            setSearchResults(data.searchResults);
            setSidebarFiles(data.sidebarFiles);
            setIsLoading(false);
          }
        })
        .catch((error) => {
          console.error('Error:', error);
        });
    } else {
      setErrorMessage("You need at least one positive example!");
    }

    console.log('results');
    console.log(result);

  }

  return (
    <div>
      {/* <p>{message}</p> */}
      <Sidebar imgsToAnnotate={sidebarFiles} allFiles={files} changeImage={changeImage} handleTextChange={handleTextChange} handleTextSubmit={handleTextSubmit} annotatedImgs={Object.keys(annotatedImages2)} />
      <NewImage image={mainImage} annotatedImgs={annotatedImages2} imgToEnvironment={message} addObject={addObject} addImage={addImage} imgDir={imgDir} />
      <SearchResults files={searchResults} changeImage={changeImage} result={result} />
      <MenuBar updateResults={updateResults} />
      {/* <button onClick={this.openBox}>Open ReactDialogBox </button> */}

      {isOpen && (
        //   <>
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
            {/* <button className="button-10" onClick={() => handleChange('wedding')}>Wedding</button> */}
            <button className="button-10" onClick={() => handleChange('receipts')}>Receipts</button>
            <button className="button-10" onClick={() => handleChange('objects')}>Objects</button>
          </div>
        </ReactDialogBox>
        //   </>
      )}
      {isLoading && (
        //   <>
        <ReactDialogBox
          // closeBox={closeBox}
          modalWidth='60%'
          // headerBackgroundColor='red'
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
        //   </>
      )}
      {(errorMessage !== "") && (
        //   <>
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
        //   </>
      )

      }
    </div>
  );
}


// class App extends Component {
//     constructor() {
//         super()
//         this.state = {
//           isOpen: true,
//           files: null,
//           mainImage: null,
//           message: fetch("/").then((reponse) => {return reponse;})
//           // message: "hi",
//         }
//       }

//       openBox = () => {
//         this.setState({
//           isOpen: true
//         })
//       }

//       closeBox = () => {
//         this.setState({
//           isOpen: false
//         })
//       }

//     handleChange = (event) => {
//         // setSelectedFiles(event.target.files);
//         this.setState({
//             isOpen: false,
//             files: event.target.files,
//             mainImage: './' + event.target.files[0].name
//           })
//       }

//     changeImage = (image) => {
//         this.setState({
//             mainImage: image
//         })
//     }


//     render() {
//         return (
//             <div>
//             <Sidebar files={this.state.files} changeImage={this.changeImage} />
//             <NewImage image={this.state.mainImage}/>
//             <SearchResults files={this.state.files} changeImage={this.changeImage}  />
//             <MenuBar/>
//             {/* <button onClick={this.openBox}>Open ReactDialogBox </button> */}

//             {this.state.isOpen && (
//             //   <>
//                 <ReactDialogBox
//                   closeBox={this.closeBox}
//                   modalWidth='60%'
//                   headerBackgroundColor='red'
//                   headerTextColor='white'
//                   headerHeight='65'
//                   closeButtonColor='white'
//                   bodyBackgroundColor='white'
//                   bodyTextColor='black'
//                   bodyHeight='200px'
//                   headerText='Title'
//                 >
//                   <div>
//                     <h1>Load Images</h1>
//                     <FileUploadButton handleChange={this.handleChange}/>
//                   </div>
//                 </ReactDialogBox>
//             //   </>
//             )}
//           </div>


//             );
//     }
// }

export default App;

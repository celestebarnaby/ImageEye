import React, {Component, useState, useEffect} from 'react';
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
  const [mainImage, setMainImage] = useState(null);
  const objectList = [];
  const annotatedImages = {};
  const [annotatedImages2, setAnnotatedImages2] = useState({});
  const [result, setResult] = useState(null);

  // Using useEffect for single rendering
  useEffect(() => {
      // Using fetch to fetch the api from 
      // flask server it will be redirected to proxy
      fetch("/data").then((res) => {
          res.json().then((data) => {
              // Setting a data from api
              setMessage(data.message);
          });
        });
  }, []);

      let openBox = () => {
        setIsOpen(true);
      };
    
      let closeBox = () => {
        setIsOpen(false);
      };

    let handleChange = (event) => {
        // setSelectedFiles(event.target.files);
        setIsOpen(false);
        setFiles(Array.from(event.target.files).map(file => './images/' + file.name))
        // setFiles(event.target.files);
        setMainImage('./images/' + event.target.files[0].name);
      };

    let changeImage = (image) => {
      setMainImage(image);
    };

    let addObject = (index) => {
      console.log(index);
      objectList.push(index);
      console.log(objectList);
      console.log('object added');
    }

    let addImage = (image) => {
      annotatedImages2[image] = objectList;
      console.log("annotated image added");
      console.log(annotatedImages2);
    }

    let updateResults = () => {
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
        setResult(data.program);
        setFiles(data.results);
      })
      .catch((error) => {
        console.error('Error:', error);
      });
    }

    console.log('files:');
    console.log(files);

  return (
        <div>
          {/* <p>{message}</p> */}
        <Sidebar files={files} changeImage={changeImage} />
        <NewImage image={mainImage} imgToEnvironment={message} addObject={addObject} addImage={addImage}/>
        <SearchResults files={files} changeImage={changeImage} result={result} />
        <MenuBar updateResults={updateResults}/>
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
                <h1>Load Images</h1>
                <FileUploadButton handleChange={handleChange}/>
              </div>
            </ReactDialogBox>
        //   </>
        )}
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

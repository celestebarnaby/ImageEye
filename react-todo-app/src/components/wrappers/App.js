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
        setFiles(event.target.files);
        setMainImage('./images/' + event.target.files[0].name);
      };

    let changeImage = (image) => {
      setMainImage(image);
    };

    console.log('hi');
    console.log(message);
    console.log(files);
    console.log(changeImage);

  return (
        <div>
          {/* <p>{message}</p> */}
        <Sidebar files={files} changeImage={changeImage} />
        <NewImage image={mainImage} imgToEnvironment={message}/>
        <SearchResults files={files} changeImage={changeImage}  />
        <MenuBar/>
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

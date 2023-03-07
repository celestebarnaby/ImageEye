import React, {Component, useState} from 'react';
import Sidebar from '../ui/Sidebar';
import NewImage from '../ui/NewImage';
import SearchResults from '../ui/SearchResults';
import MenuBar from '../ui/MenuBar';
import { ReactDialogBox } from 'react-js-dialog-box'
import 'react-js-dialog-box/dist/index.css'
import FileUploadButton from '../ui/FileUploadButton';

class App extends Component {
    constructor() {
        super()
        this.state = {
          isOpen: true,
          files: null,
          mainImage: null
        }
      }
    
      openBox = () => {
        this.setState({
          isOpen: true
        })
      }
    
      closeBox = () => {
        this.setState({
          isOpen: false
        })
      }

    handleChange = (event) => {
        // setSelectedFiles(event.target.files);
        this.setState({
            isOpen: false,
            files: event.target.files,
            mainImage: './' + event.target.files[0].name
          })
      }

    changeImage = (image) => {
        this.setState({
            mainImage: image
        })
    }


    render() {
        return (
            <div>
            <Sidebar files={this.state.files} changeImage={this.changeImage} />
            <NewImage image={this.state.mainImage}/>
            <SearchResults files={this.state.files} changeImage={this.changeImage}  />
            <MenuBar/>
            {/* <button onClick={this.openBox}>Open ReactDialogBox </button> */}
    
            {this.state.isOpen && (
            //   <>
                <ReactDialogBox
                  closeBox={this.closeBox}
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
                    <FileUploadButton handleChange={this.handleChange}/>
                  </div>
                </ReactDialogBox>
            //   </>
            )}
          </div>
        
        
            );
    }
}

export default App;

<template>
  <div id="app" class="flex flex-col h-screen bg-coolGray-100">
    <header class="bg-gray-200 text-gray-800 text-center py-4 flex justify-between items-center">
      <!-- Home Button in Header -->
      <button @click="gotoHomePage" class="home-button ml-4">
        <!-- Home Icon -->
        <img src="@/assets/home.png" alt="Home" />
      </button>
      <h1 class="font-bold text-3xl">Little AI-Assisted EPUB Reader</h1>
      <div></div> <!-- Placeholder for alignment -->
    </header>


    <main class="flex flex-grow overflow-auto p-4">
      <home-screen v-if="showHomeScreen" @selectBook="completeBookSelection"/>

      <reading-area v-else
      :book="book"
      :showBookSummary="showBookSummary"
      :bookTitle="bookTitle"
      :showChat="showChat"
      :filename="filename"
      @closeChat="handleCloseChat"
      @closeSummary="showBookSummary = false"
      @handleresize="handleResize"/>

    </main>

    <footer class="flex justify-center bg-gray-300 p-4">
      <div v-if="showHomeScreen">
        <input type="file" id="file-upload" @change="onFileUpload" hidden>
        <label for="file-upload" class="upload-button">Upload Book</label>
      </div>
      <div v-else class="footer-buttons">
        <button @click="increaseFontSize" class="button-style font-size-increase">
          A+
        </button>
        <button @click="decreaseFontSize" class="button-style font-size-decrease">
          A-
        </button>
        <button @click="openSummary" class="button-style book-summary-button">
          Book Summary
        </button>
        <button @click="displayChat" class="button-style chat-toggle-button">
          Chat with Book
        </button>
      </div>
    </footer>
  </div>
</template>

<script>
import ePub from 'epubjs';
import HomeScreen from './components/HomeScreen.vue';
import ReadingArea from './components/ReadingArea.vue';


export default {
  components: {
    HomeScreen,
    ReadingArea
  },
  name: 'App',
  data() {
    return {
      book: null,
      filename: null,
      showBookSummary: false,
      showChat: false,
      showHomeScreen: true,
      currentBookSummary: 'Default book summary',
      chapterSummaryList: [],
      rendition: null,
      fontSize: 100,
      isSidePanelOpen: false,
      bookAreaWidth: null,
      currentChapterURI: null,
      bookTitle: null,
      numberOfChapters: 0,
      currentChapterSummary: null,
      fileUploaded: false,
      epubFile: null, // Store the actual file object here
      windowSize: {
        width: window.innerWidth,
        height: window.innerHeight
      },
    };
  },
  methods: {

  onFileUpload(e) {
    const file = e.target.files[0];
    if (file && file.type === "application/epub+zip") {
      this.epubFile = file;
      this.fileUploaded = false;
      // this.chapterSummaryList = [];
      const reader = new FileReader();
      reader.readAsArrayBuffer(file);
      reader.addEventListener("load", () => {
         this.loadBook(reader.result); // reader.result contains the ArrayBuffer
      }, false);      
      this.uploadEpubFile();
      // this.showHomeScreen = false;

    } else {
      alert("Please select an EPUB file.");
    }
},

    async completeBookSelection(book) {
      await this.openSelectedBook(book);
    },

    displayChat() {
      this.showChat = true;
    },

    handleCloseChat() {
      this.showChat = false;
  },


    async openSelectedBook(book) {
      this.chapterSummaryList = [];
      this.currentBookSummary = "";

      try {
        const response = await fetch(`http://localhost:8000${book.epub}`);
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        this.filename = book.filename;
        console.log("updated this.filename", book.filename)

        const epubBlob = await response.blob();
        this.epubFile = new File([epubBlob], book.name, { type: 'application/epub+zip' });

        const processResponse = await fetch('http://localhost:8000/process-epub', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ filename: book.filename }),
        });

        if (!processResponse.ok) {
          throw new Error(`Process error! Status: ${processResponse.status}`);
        }

        // const processResult = await processResponse.json();
        // console.log('Book processing initiated:', processResult);

        // Assuming loadBook can handle a File object

        await this.loadBook(this.epubFile); 

      } catch (error) {
        console.error("Error handling EPUB file:", error);
      }
    },


    gotoHomePage() {
    location.reload();
},

    closeChat() {
      this.showChat = false;
    },

    closeSummary() {
      this.showBookSummary = false;
      this.currentBookSummary = "";
      this.chapterSummaryList = [];
    },

    openSummary() {
      this.showBookSummary = true;
    },

    getCurrentChapterURI() {
    if (this.rendition) {
      const currentLocation = this.rendition.currentLocation();
      if (currentLocation && currentLocation.start) {
         this.currentChapterURI = currentLocation.start.href; // This is the URI of the current chapter
      }
    }
    return null;
  },


    generateChapterIdentifier(chapterName) {
      // Assuming bookTitle is set when the book is loaded
      // check if chapter name is passed
      if (!chapterName) {
        return `${this.bookTitle}_Chapter_${this.currentChapterURI}`;
      }
      else {
        return `${this.bookTitle}_Chapter_${chapterName}`;
      }
    },

  async uploadEpubFile() {
    console.log('going to upload book now');
    // this.filename = book.filename;

    if (this.epubFile && this.epubFile.size > 0) {
        const formData = new FormData();
        formData.append('file', this.epubFile);

        try {
            const response = await fetch('http://localhost:8000/upload-epub', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            // await response.json(); // If you need to do something with the response, you can assign it to a variable
            const res = await response.json();
            this.filename = res.filename
            console.log('the filename', this.filename)
            this.fileUploaded = true;
        } catch (error) {
            console.error('Error:', error);
        }
    } else {
        console.error('No valid epub file to upload');
    }
    this.showHomeScreen = false;
    
  },



    handleResize() {
      if (!this.rendition || typeof this.rendition.resize !== 'function') {
        console.error("Rendition is not initialized or resize method is not available.");
        return;
      }
      // console.alert("handleResize called");
      if (this.rendition) {
        // Get the window's width and height
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;

        // Calculate the height of the header and footer
        const headerHeight = document.querySelector('header').offsetHeight;
        const footerHeight = document.querySelector('footer').offsetHeight;

        // Subtract the header and footer height from the window height
        const availableHeight = windowHeight - headerHeight - footerHeight;

        // Determine the width of the side panel
        const sidePanel = document.getElementById('side-panel');
        const sidePanelWidth = sidePanel ? sidePanel.offsetWidth : 0;

        // Check if the side panel is open and adjust the width
        const availableWidth = this.isSidePanelOpen ? windowWidth - sidePanelWidth : windowWidth;

        // Update the windowSize in your data
        this.windowSize.width = availableWidth - 300;
        this.windowSize.height = availableHeight - 200;

        // Resize the rendition to fit the new available space
        this.rendition.resize(this.windowSize.width, this.windowSize.height);
      }
},

    increaseFontSize() {
      if (this.rendition) {
        this.fontSize += 10; // increase font size by 10%
        this.rendition.themes.fontSize(`${this.fontSize}%`);
      }
    },

    decreaseFontSize() {
      if (this.rendition) {
        this.fontSize = Math.max(this.fontSize - 10, 50); // decrease font size, minimum 50%
        this.rendition.themes.fontSize(`${this.fontSize}%`);
      }
    },


  async loadBook(arrayBuffer) {
      return new Promise((resolve, reject) => {
      if (this.rendition) {
        this.rendition.destroy();
      }
      this.book = ePub(arrayBuffer);
      console.log('in this book');

      this.book.ready.then(() => {
        this.rendition = this.book.renderTo("book-area", {
          width: this.windowSize.width, 
          height: this.windowSize.height
        });

        this.book.loaded.metadata.then(metadata => {
          this.bookTitle = metadata.title; // Store the book title

          this.rendition.themes.fontSize(`${this.fontSize}%`);
          this.rendition.display();
          this.showHomeScreen = false;
          // console.log("before handle resize");
          // this.handleResize();
          // console.log("after handle resize");
          console.log("book successfully loaded", this.bookTitle);

          resolve(); // Resolve the promise when everything is done
        }).catch(error => {
          console.error("Error in metadata loading:", error);
          reject(error); // Reject the promise on error
        });

      }).catch(error => {
        console.error("Error loading book:", error);
        reject(error); // Reject the promise on error
      });
    });
  },

    prevPage() {
      if (this.rendition) {
        this.rendition.prev();
        this.getCurrentChapterURI()
      } else {
        console.error("Rendition is not initialized.");
      }
    },
    nextPage() {
      if (this.rendition) {
        this.rendition.next();
        this.getCurrentChapterURI()
        this.handleResize();
      } else {
        console.error("Rendition is not initialized.");
      }
    },

    handleKeyDown(event) {
      switch (event.key) {
        case 'ArrowRight': // Right arrow key for next page
          this.nextPage();
          break;
        case 'ArrowLeft': // Left arrow key for previous page
          this.prevPage();
          break;
        // ... handle other keys if needed ...
      }
    },


  },


  mounted() {
    this.$nextTick(() => {
      window.addEventListener('keydown', (event) => this.handleKeyDown(event));
      window.addEventListener('resize', this.handleResize);
      this.handleResize(); // Adjust this to wait for the next DOM update cycle
    });    
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize);
    window.removeEventListener('keydown', (event) => this.handleKeyDown(event));
  }
}
</script>

<style>
/* Header and Footer styling */
/* header, footer {
  background-color: #353f4c; 
  color: white;
  padding: 16px 0;
  transition: background-color 0.3s; 
} */

header {
    background-color: #f5f5f5; /* Light grey background */
    color: white; /* White text */
    /* Rest of your styles */
}

header:hover, footer:hover {
  background-color: bg-gray-800; /* Slightly lighter grey-blue on hover */
}

header h1, footer div {
  margin: 0;
  font-size: 1.8rem;
  font-weight: bold;
  text-align: center;
}

/* Main content styling */
main {
  flex-grow: 1;
  overflow: auto;
  padding: 16px;
  background-color: #f4f7fa; /* A light, neutral color for the main area */
}

/* Button styling */
.button-style {
    background-color: transparent; /* Transparent background */
    color: black; /* Black text color */
    border: 2px solid black; /* Black border */
    padding: 5px 10px; /* Padding for button size */
    margin: 0 5px; /* Margin for spacing */
    border-radius: 4px; /* Rounded corners */
    transition: all 0.3s ease; /* Smooth transition for hover effect */
}


.button-style:hover {
    color: grey; /* Grey text color on hover */
    border-color: grey; /* Grey border on hover */
}


.button-style:active {
  background-color: #87b4d6; /* Different shade for active state */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.25); /* Slightly deeper shadow for clicked state */
}

.font-size-increase, .font-size-decrease, .book-summary-button, .home-button {
  /* Optionally, you can add specific styles for each button type here */
}

/* Scrollbar styling for main area */
main::-webkit-scrollbar {
  width: 8px;
}

main::-webkit-scrollbar-thumb {
  background-color: #bdc3c7; /* Scrollbar color */
  border-radius: 8px;
}

main::-webkit-scrollbar-thumb:hover {
  background-color: #95a5a6; /* Scrollbar color on hover */
}

.upload-button {
  background-color: #3ea5e5; /* Blue color similar to the close button */
  color: white;
  cursor: pointer;
  padding: 10px 20px;
  font-weight: bold;
  border-radius: 20px; /* Rounded corners */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2); /* Shadow effect */
  transition: background-color 0.3s, transform 0.3s; /* Smooth transition for hover and click */
  display: inline-block; /* Correctly display inline with padding and border-radius */
  text-align: center;
}

.upload-button:hover {
  background-color: #a2c530; /* Darker shade for hover, similar to the close button */
  transform: scale(1.05); /* Slightly enlarge on hover */
}

.upload-button:active {
  background-color: #87b4d6; /* Different shade for active state */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.25); /* Slightly deeper shadow for clicked state */
}

.home-button {
    padding: 10px; /* Increase the padding */
    border: none; /* Optionally, remove border */
    background-color: transparent; /* Optionally, make the background transparent */
    cursor: pointer; /* Changes the cursor to indicate it's clickable */
}

.home-button img {
    width: 50px; /* Increase the size of the image */
    height: 50px; /* Maintain the aspect ratio */
    transition: transform 0.3s ease; /* Smooth transition for the hover effect */
}

.home-button:hover img {
    transform: scale(1.2); /* Slightly increase the image size on hover */
    /* You can add additional effects like changing the image, border, or background here */
}

.footer-buttons {
    display: flex; /* Enables flexbox */
    align-items: center; /* Aligns items vertically in the center */
    justify-content: center; /* Center the items horizontally */
}

.font-size-increase,
.font-size-decrease {
    margin: 0 5px; /* Small margin for spacing between font size buttons */
}

.font-size-decrease {
    margin-right: 60px; /* Additional margin to the right of the decrease font size button */
}

</style>

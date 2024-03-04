<template>
  <div id="app" class="flex flex-col h-screen bg-coolGray-100">
    <header class="bg-indigo-700 text-white text-center py-4">
      <h1 class="font-bold text-3xl">My little AI-Assisted EPUB Reader</h1>
    </header>

    <main class="flex flex-grow overflow-auto p-4">
      <home-screen v-if="showHomeScreen" @selectBook="completeBookSelection" @fileSelected="uploadBook"/>

      <reading-area v-else
      :book="book"
      :showBookSummary="showBookSummary"
      :bookTitle="bookTitle"
      @closeSummary="showBookSummary = false"
      @handleresize="handleResize"/>

    </main>

    <footer class="flex justify-center bg-purple-800 p-4">
      <!-- Conditional Footer content -->
      <div v-if="showHomeScreen">
        <!-- Buttons for Home Screen -->
        <!-- Upload EPUB File Button -->
        <!-- <input type="file" id="file-input" hidden @change="handleFileChange" accept=".epub"/> -->
        
        <input type="file" id="file-upload" @change="onFileChange" hidden>
        <label for="file-upload" class="upload-button">Upload File</label>

        <!-- <input type="file" @change="onFileChange" class="bg-emerald-500 hover:bg-emerald-700 text-white font-semibold py-2 px-4 rounded"> -->
        <!-- <button @click="uploadEpubFile" class="bg-emerald-500 hover:bg-emerald-700 text-white font-semibold py-2 px-4 rounded">
        
          Upload EPUB File
        </button> -->
      </div>
      <div v-else>
        <!-- Buttons for Reading Area -->
        <!-- Increase / Decrease Font Size Buttons -->
        <button @click="increaseFontSize" class="button-style font-size-increase">
          A+
        </button>
        <button @click="decreaseFontSize" class="button-style font-size-decrease">
          A-
        </button>
        <!-- Book Summary Button -->
        <button @click="openSummary" class="button-style book-summary-button">
          Book Summary
        </button>
        <button @click="gotoHomePage" class="button-style home-button">
          Home
        </button>
      </div>
    </footer>

    <!-- Home Button (Top Left of the Screen) -->

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
      showBookSummary: false,
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

    onFileChange(e) {
    const file = e.target.files[0];
    if (file && file.type === "application/epub+zip") {
      this.epubFile = file;
      this.fileUploaded = false;
      this.chapterSummaryList = [];
      this.showHomeScreen = false;
      const reader = new FileReader();
      reader.addEventListener("load", () => {
        this.loadBook(reader.result); // reader.result contains the ArrayBuffer
      }, false);
      reader.readAsArrayBuffer(file);
      this.uploadEpubFile();

    } else {
      alert("Please select an EPUB file.");
    }
},


    // async completeBookSelection(book) {

    //   await this.openSelectedBook(book);
    //   console.log("fuck yeah");
    //   this.showHomeScreen = false;
    //   // on nexttick handle resize
    //   this.$nextTick(() => {
    //     this.handleResize();
    //   });
    // },

    async completeBookSelection(book) {
      await this.openSelectedBook(book);

      this.showHomeScreen = false; // This line triggers DOM changes

      // Ensure handleResize is called in the next tick, after the DOM updates
      this.$nextTick(() => {
        try {
          if (this.rendition) {
            // this.handleResize(); // Call this only if rendition object is available
          } else {
            console.error("Rendition object is not available");
          }
        } catch (error) {
          console.error("Error occurred during handleResize:", error);
        }
      });
    },

    async openSelectedBook(book) {
      
      this.chapterSummaryList = [];
      this.currentBookSummary = "";

      try {
        const response = await fetch(`http://localhost:8000${book.epub}`);
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const epubBlob = await response.blob();
        this.epubFile = new File([epubBlob], book.name, { type: 'application/epub+zip' });
        await this.loadBook(this.epubFile); // Assuming loadBook can handle a File object
        // after nexttick do handleresize
        // this.showHomeScreen = false;
        // this.$nextTick(() => {
        //   this.handleResize();
        // });
      } catch (error) {
        console.error("Error fetching EPUB file:", error);
      }
      
      // this.getBookSummary()
    },

    uploadBook(e) {
      const file = e.target.files[0];
      if (file && file.type === "application/epub+zip") {
        this.epubFile = file;
        this.fileUploaded = false;
        this.chapterSummaryList = [];
        const reader = new FileReader();
        reader.addEventListener("load", () => {
          this.loadBook(reader.result); // reader.result contains the ArrayBuffer
        }, false);
        reader.readAsArrayBuffer(file);
      } else {
        alert("Please select an EPUB file.");
      }
    },

    gotoHomePage() {
      this.showHomeScreen = true;
      this.$nextTick(() => {
    // Call handleResize after Vue has updated the DOM
        //this.handleResize();
      });
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

      constructBookSummary() {
      // Construct the book summary from the chapter summaries
      this.currentBookSummary = "";
      for (let chapterSummary of this.chapterSummaryList) {
        // {is_main_content: 'Yes', summary: "This chapter gives insights into the book 'Make So…s' with a mention of the Steve Jobs Archive logo.", title: 'Chapter: Make Something Wonderful: Steve Jobs in his own words'}
        this.currentBookSummary += `<strong>${chapterSummary.summary.title}</strong>: ${chapterSummary.summary.summary}<br><br>`;
      }
    },

    // aiAssist() {
    //   // Step 3: Implement sending the EPUB file to the server
    //   if (this.fileUploaded == false) {
    //     this.uploadEpubFile();
    //     console.log("going to upload file");
    //   }
    //   else {
    //     console.log("not going to upload again");
    //   }
    //   // Step 4: Open the side panel
    //   this.toggleSidePanel();

    //   // Step 5: Resize the book rendition
    //   this.handleResize();

    //   this.getCurrentChapterURI()
    // },

    async getBookSummary() {
      // This function populates the chapterSummaryList array with the chapter summaries
      // Get the list of chapters
      if (!this.book) {
        console.error("Book not loaded");
        return;
      }
      if (this.fileUploaded == false) {
        // The following line triggers the book_main using upload epub API call
        this.uploadEpubFile();
      }
      let chapters = await this.book.spine.spineItems;
      
      for (let chapter of chapters) {
        await this.fetchChapterSummary(chapter.href);
      }
      this.constructBookSummary();

    },


    fetchChapterSummary(chapterHref) {
        return new Promise((resolve, reject) => {
          // create endpoint combining book title and chapter href
          const chapterIdentifier = this.generateChapterIdentifier(chapterHref);
          const url = `http://localhost:8000/chapter-summary/${encodeURIComponent(chapterIdentifier)}`;
          let attempts = 0;

          const pollForSummary = () => {
            fetch(url)
              .then(response => {
                if (!response.ok) {
                  throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
              })
              .then(data => {
                if (data.status === "success") {
                  // push the summary as a map with keys as chapter title and summary
                  this.chapterSummaryList.push({chapter: chapterHref, summary: data.chapter_summary});
                  //this.chapterSummaryList.push(data.chapter_summary);
                  resolve();
                } else if (data.status === "pending") {
                  attempts++;
                  if (attempts < 5) { // Retry up to 5 times
                    setTimeout(pollForSummary, 5000); // Poll every 5 seconds
                  } else {
                    console.log(`Maximum retries reached for ${chapterHref}`);
                    reject(new Error(`Maximum retries reached for ${chapterHref}`));
                  }
                } else {
                  
                  console.error(`Error fetching summary for ${chapterHref}:`, data.message);
                  resolve();
                }
              })
              .catch(error => {
                console.log('some error here')
                console.error(`Error in fetching chapter summary for ${chapterHref}:`, error.message);
                resolve();
              });
          };

          pollForSummary();
        });
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

    showChapterSummary() {
      const chapterIdentifier = this.generateChapterIdentifier();
      console.log(`Fetching summary for chapter: ${chapterIdentifier}`);

      // URL of your Flask endpoint
      const url = `http://localhost:8000/chapter-summary/${encodeURIComponent(chapterIdentifier)}`;

      // Make the HTTP GET request
      fetch(url)
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          if (data.status === "success") {
            // Handle the retrieved summary
            console.log("Chapter Summary:", data.chapter_summary);
            this.currentChapterSummary = data.chapter_summary
            // You might want to update some data property or state with this summary
            // For example: this.currentChapterSummary = data.chapter_summary;
          } else {
            console.error("Error fetching summary:", data.message);
          }
        })
        .catch(error => {
          console.error("Error in fetching chapter summary:", error.message);
        });
    },

    showAIExplanation() {
      // Logic to show AI explanation
      console.log('AI Explanation button clicked');
    },

    toggleSidePanel() {
      this.isSidePanelOpen = !this.isSidePanelOpen; // Toggle the state
      //this.resizeBookForSidePanel(); // Resize accordingly
    },


    resizeBookForSidePanel() {
    const sidePanelWidth = this.isSidePanelOpen ? 300 : 0; // Assuming 300px width for the side panel
    this.bookAreaWidth = window.innerWidth - sidePanelWidth;

    if (this.rendition) {
      this.rendition.resize(this.bookAreaWidth, this.windowSize.height);
    }
  },

  uploadEpubFile() {
    // Check if this.epubFile is a File object and has a size greater than 0
    console.log('going to upload book now')
    if (this.epubFile && this.epubFile.size > 0) {
      const formData = new FormData();
      formData.append('file', this.epubFile); // Assuming this.epubFile holds the file object

      fetch('http://localhost:8000/upload-epub', {
        method: 'POST',
        body: formData,
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        console.log('File upload Success:', data);
        this.fileUploaded = true;
      })
      .catch((error) => {
        console.error('Error:', error);
      });
    } else {
      console.error('No valid epub file to upload');
    }
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

    // loadBook(arrayBuffer) {
    //   if (this.rendition) {
    //     this.rendition.destroy();
    //   }
    //   this.book = ePub(arrayBuffer);
    //   console.log("Book after loading:", this.book);
    //   this.book.ready.then(() => {
    //     this.rendition = this.book.renderTo("book-area", {
    //       width: this.windowSize.width, 
    //       height: this.windowSize.height
    //     });
    //     this.book.loaded.metadata.then(metadata => {
    //     this.bookTitle = metadata.title; // Store the book title in the component's data
    //     console.log("Book title:", this.bookTitle);
    //     })
    //     this.rendition.themes.fontSize(`${this.fontSize}%`);
    //     this.rendition.display();
    //     // resize after nextick

    //     this.handleResize();
        
    //   }).catch(error => {
    //     console.error("Error loading book:", error);
    //   });
    // },

  loadBook(arrayBuffer) {
      return new Promise((resolve, reject) => {
      if (this.rendition) {
        this.rendition.destroy();
      }
      this.book = ePub(arrayBuffer);

      this.book.ready.then(() => {
        this.rendition = this.book.renderTo("book-area", {
          width: this.windowSize.width, 
          height: this.windowSize.height
        });

        this.book.loaded.metadata.then(metadata => {
          this.bookTitle = metadata.title; // Store the book title
          console.log("Book title:", this.bookTitle);

          this.rendition.themes.fontSize(`${this.fontSize}%`);
          this.rendition.display();
          // console.log("before handle resize");
          // this.handleResize();
          // console.log("after handle resize");

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
header, footer {
  background-color: #353f4c; /* A deep, professional grey-blue */
  color: white;
  padding: 16px 0;
  transition: background-color 0.3s; /* Smooth transition for hover effect */
}

header:hover, footer:hover {
  background-color: #3e4a59; /* Slightly lighter grey-blue on hover */
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
  background-color: #3ea5e5; /* Blue color similar to the upload button */
  color: white;
  cursor: pointer;
  padding: 10px 20px;
  font-weight: bold;
  border-radius: 20px; /* Rounded corners */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2); /* Shadow effect */
  transition: background-color 0.3s, transform 0.3s; /* Smooth transition for hover and click */
  border: none; /* No border */
  text-align: center;
}

.button-style:hover {
  background-color: #a2c530; /* Darker shade for hover */
  transform: scale(1.05); /* Slightly enlarge on hover */
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

</style>

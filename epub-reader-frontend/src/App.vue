<template>
  <div id="app" class="flex flex-col h-screen bg-coolGray-100">
    <header class="bg-indigo-700 text-white text-center py-4">
      <h1 class="font-bold text-3xl">My little AI-Assisted EPUB Reader</h1>
    </header>

    <main :class="isSidePanelOpen ? 'flex-row' : 'flex-col'" class="flex flex-grow overflow-auto p-4">
      <div id="book-area" :class="isSidePanelOpen ? 'flex-grow' : 'w-full'" class="bg-white shadow-md rounded p-4">
        <!-- Book content here -->
      </div>
      <div v-if="showBookSummary" class="overlay bg-black bg-opacity-75 fixed inset-0 flex justify-center items-center">
        <div class="overlay-content">
          <h2>Book Summary</h2>
          <p>{{ currentBookSummary }}</p>
          <button @click="toggleBookSummary" class="close-button">Close</button>
        </div>
      </div>
      <div v-if="isSidePanelOpen" id="side-panel" class="w-custom bg-lightBlue-500 rounded text-black p-4">

        <h2 class="font-semibold text-lg mb-4">AI Insights</h2>
            <!-- Chapter Summary Button -->
            <button @click="showChapterSummary" class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded block mb-2">
              Chapter Summary
            </button>
            <!-- Chapter Summary Display -->
            <div v-if="currentChapterSummary" class="chapter-summary">
              <h5 class="font-semibold">Chapter Summary:</h5>
              <p>{{ currentChapterSummary }}</p>
            </div>
            <!-- AI Explanation Button -->
            <button @click="showAIExplanation" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded block">
              AI Explanation
            </button>
      </div>
    </main>

    <footer class="flex justify-center bg-purple-800 p-4">
      <div class="button-group space-x-2">
        <button @click="prevPage" class="bg-purple-500 hover:bg-purple-700 text-white font-semibold py-2 px-4 rounded">
          Previous
        </button>
        <button @click="nextPage" class="bg-purple-500 hover:bg-purple-700 text-white font-semibold py-2 px-4 rounded">
          Next
        </button>
        <button @click="decreaseFontSize" class="bg-violet-500 hover:bg-violet-700 text-white font-semibold py-2 px-4 rounded">
          A-
        </button>
        <button @click="increaseFontSize" class="bg-violet-500 hover:bg-violet-700 text-white font-semibold py-2 px-4 rounded">
          A+
        </button>
        <input type="file" @change="onFileChange" class="bg-emerald-500 hover:bg-emerald-700 text-white font-semibold py-2 px-4 rounded">
        <button @click="loadDefaultBook" class="bg-emerald-500 hover:bg-emerald-700 text-white font-semibold py-2 px-4 rounded">
          Load Default Book
        </button>
        <button @click="booksummary" class="bg-amber-500 hover:bg-amber-700 text-white font-semibold py-2 px-4 rounded">
          Book Summary
        </button>
        <button @click="aiAssist" class="bg-amber-500 hover:bg-amber-700 text-white font-semibold py-2 px-4 rounded">
          AI Assistance
        </button>
      </div>
    </footer>
  </div>
</template>


<style>
.flex-grow {
  transition: all 0.3s ease;
}

.limited-width {
  max-width: 75%; /* Adjust as necessary */
  transition: all 0.3s ease;
}
</style>



<script>
import ePub from 'epubjs';

export default {
  name: 'App',
  data() {
    return {
      book: null,
      showBookSummary: false,
      currentBookSummary: 'Default book summary',
      rendition: null,
      fontSize: 100,
      isSidePanelOpen: false,
      bookAreaWidth: null,
      currentChapterURI: null,
      bookTitle: null,
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

    getCurrentChapterURI() {
    if (this.rendition) {
      const currentLocation = this.rendition.currentLocation();
      if (currentLocation && currentLocation.start) {
         this.currentChapterURI = currentLocation.start.href; // This is the URI of the current chapter
         console.log("Current chapter URI:", this.currentChapterURI);
      }
    }
    return null;
  },

    aiAssist() {
      // Step 3: Implement sending the EPUB file to the server
      if (this.fileUploaded == false) {
        this.uploadEpubFile();
        console.log("going to upload file");
      }
      else {
        console.log("not going to upload again");
      }
      // Step 4: Open the side panel
      this.toggleSidePanel();

      // Step 5: Resize the book rendition
      this.handleResize();

      this.getCurrentChapterURI()
    },

    booksummary() {
      // Step 3: Implement sending the EPUB file to the server
      if (this.fileUploaded == false) {
        this.uploadEpubFile();
        console.log("going to upload file in booksummary");
      }
      else {
        console.log("not going to upload again");
      }
      this.showBookSummary = true;
      // Fetch the book summary from the server
      const url = `http://localhost:8000/book-summary/${encodeURIComponent(this.bookTitle)}`;
      fetch(url)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          console.log('Book Summary:', data.book_summary);
          this.currentBookSummary = data.book_summary;
        })
        .catch(error => {
          console.error('Error fetching book summary:', error);
        });
    },

    toggleBookSummary() {
      this.showBookSummary = !this.showBookSummary;
    },

    generateChapterIdentifier() {
      // Assuming bookTitle is set when the book is loaded
      return `${this.bookTitle}_Chapter_${this.currentChapterURI}`;
    },

    showChapterSummary() {
      const chapterIdentifier = this.generateChapterIdentifier();
      console.log(`Fetching summary for chapter: ${chapterIdentifier}`);

      // URL of your Flask endpoint
      const url = `http://localhost:8000/get-summary/${encodeURIComponent(chapterIdentifier)}`;

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

    // showChapterSummary() {
    //   // Logic to show chapter summary
    //   console.log('Chapter Summary button clicked');
    // },
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
        console.log('Success:', data);
        this.fileUploaded = true;
      })
      .catch((error) => {
        console.error('Error:', error);
      });
    } else {
      console.error('No valid epub file to upload');
    }
  },


  onFileChange(e) {
    const file = e.target.files[0];
    if (file && file.type === "application/epub+zip") {
      this.epubFile = file;
      this.fileUploaded = false;
      console.log("File uploaded bool:", this.fileUploaded);
      const reader = new FileReader();
      reader.addEventListener("load", () => {
        this.loadBook(reader.result); // reader.result contains the ArrayBuffer
      }, false);
      reader.readAsArrayBuffer(file);
    } else {
      alert("Please select an EPUB file.");
    }
},


    // handleResize() {
    //   console.log("Rendition in handleResize:", this.rendition);
    //   if (this.rendition) {
    //     this.windowSize.width = window.innerWidth;
    //     this.windowSize.height = window.innerHeight;
    //     this.rendition.resize(this.windowSize.width, this.windowSize.height);
    //   }
    // },



    handleResize() {
      console.log("Rendition in handleResize:", this.rendition);
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
        console.log("width and height:", this.windowSize.width, this.windowSize.height);
        this.rendition.resize(this.windowSize.width, this.windowSize.height);
      }
},


    loadDefaultBook() {
      if (this.rendition) {
        this.rendition.destroy();
      }
      const defaultBookPath = "/Heart-of-Darkness.epub";

      fetch(defaultBookPath)
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.blob();
        })
        .then(blob => {
          this.epubFile = new File([blob], "Heart-of-Darkness.epub", { type: 'application/epub+zip' });
          return blob.arrayBuffer(); // Convert the Blob to an ArrayBuffer
        })
        .then(arrayBuffer => {
          this.loadBook(arrayBuffer); // Load the book using the ArrayBuffer
          this.handleResize();
        })
        .catch(error => {
          console.error("Error loading default book:", error);
        });
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

    loadBook(arrayBuffer) {
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
        this.bookTitle = metadata.title; // Store the book title in the component's data
        console.log("Book title:", this.bookTitle);
        })
        this.rendition.themes.fontSize(`${this.fontSize}%`);
        this.rendition.display();
        console.log("Rendition after display:", this.rendition);
        this.handleResize();
        
      }).catch(error => {
        console.error("Error loading book:", error);
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
      // this.loadDefaultBook(); // Load the default book on component mount
      window.addEventListener('keydown', (event) => this.handleKeyDown(event));
      window.addEventListener('resize', this.handleResize);
      this.handleResize(); // Adjust this to wait for the next DOM update cycle
      this.loadDefaultBook(); // Load the default book on component mount

      // this.loadDefaultBook(); // Load the default book on component mount
      //this.loadDefaultBook(); // Load the default book on component mount

    });    
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize);
    window.removeEventListener('keydown', (event) => this.handleKeyDown(event));
  }
}
</script>

<style>
</style>



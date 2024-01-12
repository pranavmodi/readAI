<template>
  <div id="app" class="flex flex-col h-screen bg-coolGray-100">
    <header class="bg-indigo-700 text-white text-center py-4">
      <h1 class="font-bold text-3xl">My AI-Assisted EPUB Reader</h1>
    </header>

    <main :class="isSidePanelOpen ? 'flex-row' : 'flex-col'" class="flex flex-grow overflow-auto p-4">
      <div id="book-area" :class="isSidePanelOpen ? 'flex-grow' : 'w-full'" class="bg-white shadow-md rounded p-4">
        <!-- Book content here -->
      </div>
      <div v-if="isSidePanelOpen" class="w-80 bg-lightBlue-500 rounded text-black p-4">
        <h2 class="font-semibold text-lg mb-4">AI Insights</h2>
        <div class="ai-content">
          <p>Here's some AI-generated insight based on your current reading.</p>
        </div>
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
      rendition: null,
      fontSize: 100,
      isSidePanelOpen: false,
      bookAreaWidth: null,
      fileUploaded: false,
      epubFile: null, // Store the actual file object here
      windowSize: {
        width: window.innerWidth,
        height: window.innerHeight
      },
    };
  },
  methods: {

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
      this.resizeBookForSidePanel();
    },

    toggleSidePanel() {
    this.isSidePanelOpen = !this.isSidePanelOpen; // Toggle the state
    this.resizeBookForSidePanel(); // Resize accordingly
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


    handleResize() {
      console.log("Rendition in handleResize:", this.rendition);
      if (this.rendition) {
        this.windowSize.width = window.innerWidth;
        this.windowSize.height = window.innerHeight;
        this.rendition.resize(this.windowSize.width, this.windowSize.height);
      }
    },

    loadDefaultBook() {
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
        this.rendition.themes.fontSize(`${this.fontSize}%`);
        this.rendition.display();
        console.log("Rendition after display:", this.rendition);
        //this.handleResize();
        window.addEventListener('resize', this.handleResize);
      }).catch(error => {
        console.error("Error loading book:", error);
      });
    },

    prevPage() {
      if (this.rendition) {
        this.rendition.prev();
      } else {
        console.error("Rendition is not initialized.");
      }
    },
    nextPage() {
      if (this.rendition) {
        this.rendition.next();
      } else {
        console.error("Rendition is not initialized.");
      }
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.loadDefaultBook(); // Load the default book on component mount
      //window.addEventListener('resize', this.handleResize);
      //this.handleResize(); // Adjust this to wait for the next DOM update cycle
    });    
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize);
  }
}
</script>

<style>
</style>



<template>
  <div id="app" class="flex flex-col h-screen">
    <header class="bg-gray-800 text-white text-center p-4">
      <h1>My EPUB Reader</h1>
    </header>
    <main :class="{ 'flex-grow': !isSidePanelOpen, 'limited-width': isSidePanelOpen }" class="overflow-auto">
      <div id="book-area" :style="{ width: bookAreaWidth + 'px' }" class="h-full"></div>
      <div v-if="isSidePanelOpen" class="side-panel">
        <!-- Content of the side panel goes here -->
      </div>
    </main>

    <footer class="flex justify-center bg-gray-200 p-4">
      <button @click="prevPage" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mr-2">
        Previous
      </button>
      <button @click="nextPage" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
        Next
      </button>
      <button @click="decreaseFontSize" class="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded mr-2">
    A-
  </button>
  <button @click="increaseFontSize" class="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded">
    A+
  </button>
  <div class="flex justify-center p-4">
      <input type="file" @change="onFileChange" class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
      <button @click="loadDefaultBook" class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
        Load Default Book
      </button>
    </div>
    <button @click="aiAssist" class="bg-orange-500 hover:bg-orange-700 text-white font-bold py-2 px-4 rounded">
    AI Assistance
  </button>
    </footer>

  </div>

</template>


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
      this.openSidePanel();

      // Step 5: Resize the book rendition
      this.resizeBookForSidePanel();
    },

    openSidePanel() {
      this.isSidePanelOpen = true;
      this.resizeBookForSidePanel(); // Resize when the panel is opened
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
.flex-grow {
  /* CSS rules for normal state */
}

.limited-width {
  /* CSS rules to limit width when side panel is open */
}
</style>



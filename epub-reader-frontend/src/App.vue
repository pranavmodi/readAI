<template>
  <div id="app">
    <header>
      <h1>My EPUB Reader</h1>
    </header>
    <main>
      <div id="book-area"></div>
    </main>
    <footer>
      <button @click="prevPage">Previous</button>
      <button @click="nextPage">Next</button>
    </footer>
    <input type="file" @change="onFileChange">
    <button @click="loadDefaultBook">Load Default Book</button>
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
        const url = URL.createObjectURL(file);
        this.loadBook(url);
      } else {
        alert("Please select an EPUB file.");
      }
    },
    handleResize() {
      this.windowSize.width = window.innerWidth;
      this.windowSize.height = window.innerHeight;
      if (this.rendition) {
        this.rendition.resize(this.windowSize.width, this.windowSize.height);
      }
    },
    loadDefaultBook() {
      const defaultBookPath = "/Heart-of-Darkness.epub";
      this.loadBook(defaultBookPath);
    },
    loadBook(url) {
      this.book = ePub(url);
      this.book.ready.then(() => {
        // Set the rendition to the full window size
        this.rendition = this.book.renderTo("book-area", {
          width: window.innerWidth, 
          height: window.innerHeight
        });
        this.rendition.display();
        this.handleResize(); // Handle initial sizing
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
      window.addEventListener('resize', this.handleResize);
      this.handleResize(); // Adjust this to wait for the next DOM update cycle
    });    
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize);
  }
}
</script>

<style>
#book-area {
  width: 100vw;
  height: 100vh;
  /* Add additional styling as needed */
}
/* You might want to style the body or the main container to ensure it takes full height */
html, body, #app {
  height: 100vh;
  margin: 0;
  padding: 0;
}
</style>


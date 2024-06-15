<template>
  <div class="home-screen flex flex-col items-center justify-center">
    <div class="grid-container overflow-auto">
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-4 gap-4 my-4" style="width: fit-content; margin: auto;">
        <div v-for="book in books" :key="book.name" class="book-thumbnail flex flex-col items-center h-full" @click="selectBook(book)">
          <img :src="book.thumbnail" :alt="`Cover of ${book.name}`" class="w-auto h-96 rounded-lg shadow-md object-cover"/>
          <h3 class="text-center mt-2">{{ book.name }}</h3>
        </div>
      </div>
    </div>
  </div>
</template>

  
  <script>
  import axios from 'axios';
  axios.defaults.baseURL = 'http://localhost:8000/';
  
  export default {
    data() {
      return {
        books: []
      };
    },
    props: ['booksUrl'],
    methods: {
      selectBook(book) {
        this.$emit('selectBook', book);
      },
      
      fetchBooks() {
        axios.get("/get-books")
          .then(response => {
            this.books = response.data.map(book => {
              return {
                ...book,
                thumbnail: `http://localhost:8000${book.thumbnail}`
              };
            });
          })
          .catch(error => {
            console.error("Error fetching books:", error);
          });
      }, 

      onFileChange(event) {
      // Check if files are selected
      console.log("mothafucka File selected");
      if (event.target.files && event.target.files.length > 0) {
        // Get the first file (since you're only interested in one file)
        // const file = event.target.files[0];

        // Emit an event to the parent component with the selected file
        this.$emit('fileSelected', event);
      }
    },
    }, // This is where the methods object ends


  
    mounted() {
      this.fetchBooks();
    }
  }
  </script>
  
  
  <style scoped>
.book-thumbnail {
  cursor: pointer;
  transition: transform 0.3s ease;
  display: flex; /* Flex display */
  flex-direction: column; /* Stack children vertically */
  justify-content: center; /* Center content vertically */
  align-items: center; /* Center content horizontally */
  height: 100%; /* Full height */
}

.book-thumbnail:hover {
  transform: translateY(-20px);
}

.grid-container {
  padding-top: 20px; /* Adjust this value as needed */
  padding-bottom: 20px; /* Adjust this value as needed */
  max-height: 100vh; /* Ensure it does not exceed the viewport height */
}

.upload-button {
  background-color: #4caf50; /* Green background */
  color: white; /* White text */
  padding: 10px 20px; /* Padding */
  border: none; /* No border */
  border-radius: 5px; /* Rounded corners */
  cursor: pointer; /* Pointer cursor on hover */
  font-size: 16px; /* Font size */
  transition: background-color 0.3s; /* Smooth background color transition */
}

.upload-button:hover {
  background-color: #45a049; /* Darker green background on hover */
}
  </style>
  
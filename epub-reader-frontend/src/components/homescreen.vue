<template>
  <div class="home-screen flex justify-center">
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4" style="margin: auto;">
      <div v-for="book in books" :key="book.name" class="book-thumbnail flex flex-col items-center h-full" @click="selectBook(book)">
        <img :src="book.thumbnail" :alt="`Cover of ${book.name}`" class="w-full h-auto rounded-lg shadow-md object-cover" style="height: 400px;"/> <!-- Fixed height for images -->
        <h3 class="text-center mt-2">{{ book.name }}</h3>
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
        console.log(this.booksUrl);
        console.log("Fetching books");
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
      }
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
  transform: translateY(-5px);
}
  </style>
  
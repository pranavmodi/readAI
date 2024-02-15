<template>
    <div class="home-screen">
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div v-for="book in books" :key="book.name" class="book-thumbnail" @click="selectBook(book)">
          <img :src="book.thumbnail" :alt="`Cover of ${book.name}`" class="w-full h-auto rounded-lg shadow-md"/>
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
        console.log("Fetching mothafucka books");
        axios.get("http://localhost:8000/get-books/")
          .then(response => {
            this.books = response.data;
          })
          .catch(error => {
            console.error("Error fetching books:", error);
          });
      }
    },
    mounted() {
      this.fetchBooks();
    }
  }
  </script>
  
  <style scoped>
  .book-thumbnail {
    cursor: pointer;
    transition: transform 0.3s ease;
  }
  
  .book-thumbnail:hover {
    transform: translateY(-5px);
  }
  </style>
  
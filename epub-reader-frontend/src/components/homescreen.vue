<template>
    <div class="home-screen">
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div v-for="book in books" :key="book.id" class="book-thumbnail" @click="selectBook(book)">
          <img :src="book.thumbnail" alt="Book cover" class="w-full h-auto rounded-lg shadow-md"/>
          <h3 class="text-center mt-2">{{ book.title }}</h3>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: ['books'],
    methods: {
      selectBook(book) {
        this.$emit('selectBook', book);
      }
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
  
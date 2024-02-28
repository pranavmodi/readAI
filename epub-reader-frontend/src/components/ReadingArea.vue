<template>
    <div class="reading-area flex flex-col items-center justify-center">
      <div id="book-area" class="bg-white shadow-md rounded p-4">
        <!-- Book reading area content -->
      </div>
  
      <!-- Other buttons and functionality specific to reading a book -->
      <div class="button-group space-x-2">
        <!-- Buttons for navigation, font size adjustment, etc. -->
      </div>
  
      <button @click="closeBook" class="bg-amber-500 hover:bg-amber-700 text-white font-semibold py-2 px-4 rounded">
        Close Book
      </button>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      selectedBook: Object
    },
    methods: {
      closeBook() {
        this.$emit('closeBook');
      }
    }
  };
  </script>
  
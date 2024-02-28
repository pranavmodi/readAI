<template>
    <div class="reading-area flex flex-col items-center justify-center">
        <!-- if showsummary is not true show book-area -->
      <div id="book-area" class="bg-white shadow-md rounded p-4">
      </div>

      <div v-if="showBookSummary" class="overlay bg-black bg-opacity-100 fixed inset-0 flex justify-center items-center transition-opacity ease-out duration-300">
        <div class="overlay-content bg-white p-6 rounded-lg shadow-xl w-full sm:w-3/4 md:w-1/2">
          <h2 class="text-2xl md:text-3xl font-bold text-gray-800 mb-4">Book Summary</h2>
          <div class="summary-text" style="max-height: 70vh; overflow: auto;">
            <div v-html="currentBookSummary"></div>
          </div>
          <button @click="closeSummary" class="bg-red-500 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded transition duration-300 ease-in-out">
            Close
          </button>
        </div>
      </div>
  
      <!-- Other buttons and functionality specific to reading a book -->
      <div class="button-group space-x-2">
        <!-- Buttons for navigation, font size adjustment, etc. -->
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: {
        selectedBook: Object,
        showBookSummary: Boolean,
        currentBookSummary: String,
    },
    data() {
    return {
        // currentBookSummary: "Default Summary",
    };
  },
    methods: {
        closeSummary() {
            this.$emit("closeSummary");            
        },

        onShowBookSummaryChanged(newValue) {
            if (newValue) {
                console.log("showsummary turned true");
            }
        }
    },
    watch: {
            showBookSummary(newValue) {
            this.onShowBookSummaryChanged(newValue);
        },
        // other methods...
    },
  };
  </script>
  
<template>
<div class="reading-area flex flex-col items-center justify-center">
    <!-- if showsummary is not true show book-area -->
    <div id="book-area" class="bg-white shadow-md rounded p-4">
    </div>

    <div v-if="showBookSummary" class="overlay bg-black bg-opacity-100 fixed inset-0 flex justify-center items-center transition-opacity ease-out duration-300">
        <div class="overlay-content bg-white p-6 rounded-lg shadow-xl w-full sm:w-3/4 md:w-1/2">
          
          <!-- Styled Toggle Switch -->
          <div class="toggle-switch mb-4">
              <input type="radio" id="bookSummary" name="summaryType" value="book" v-model="selectedSummaryType">
              <label for="bookSummary">Book Summary</label>
              
              <input type="radio" id="chapterSummary" name="summaryType" value="chapter" v-model="selectedSummaryType">
              <label for="chapterSummary">Chapter Summaries</label>
          </div>

          <!-- <h2 class="text-2xl md:text-3xl font-bold text-gray-800 mb-4">Summary</h2> -->
          <div class="summary-text" style="max-height: 70vh; overflow: auto;">
              <!-- Render each chapter summary -->
              <div v-for="summary in currentSummaries" class="chapter-summary">
                <h3>{{ summary.title }}</h3>
                <p>{{ summary.content }}</p>
              </div>
          </div>
          <button @click="closeSummary" class="close-button text-white font-semibold py-2 px-4 rounded transition duration-300 ease-in-out">
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

  import axios from 'axios';
  axios.defaults.baseURL = 'http://localhost:8000/';

  export default {
    props: {
        selectedBook: Object,
        showBookSummary: Boolean,
        bookTitle: String,
        currentChapterURI: String
    },
    data() {
    return {
        selectedSummaryType: "book",
        currentBookSummary: "Default Summary",
        currentChapterSummaries: "Default Chapter Summaries",
        currentSummaries: [],
    };
  },
    methods: {
        closeSummary() {
            this.$emit("closeSummary");
            this.currentBookSummary = "";
            this.currentChapterSummaries = "";            
        },

        constructBookSummary() {
            // Assuming chapterSummaryList is an array of chapter summary objects
            // No need to concatenate strings, as we will use a Vue template to render them
            this.currentBookSummaries = this.chapterSummaryList.map(chapter => ({
            title: chapter.summary.title,
            content: chapter.summary.summary
            }));
        },

        onShowBookSummaryChanged(newValue) {
            if (newValue) {
                console.log("showsummary turned true");
            }
        },
        
        getBookSummary() {
            console.log("Getting book summary");
            const encodedBookTitle = encodeURIComponent(this.bookTitle);

            axios.get(`/book-summary/${encodedBookTitle}`)
                .then(response => {
                    this.currentBookSummary = response.data.book_summary;
                    this.currentSummaries = [{ 
                        title: "Book Summary", 
                        content: this.currentBookSummary 
            }];
                })
                .catch(error => {
                    console.error("Error fetching book summary:", error);
                    // Handle the error. For example, you might want to show an error message to the user.
                });

            // set the first element of currentSummaries to currentBookSummary
        },

        getChapterSummaries() {
            this.currentSummaries = [];
            console.log("Getting chapter summaries");
        },
    },
    watch: {
            showBookSummary(newValue) {
            this.onShowBookSummaryChanged(newValue);

        },
            selectedSummaryType(newValue) {
            console.log("Selected summary type changed to:", newValue);
            if (newValue === "book") {
                this.getBookSummary();
            } else {
                this.getChapterSummaries();
            }
        }
    },
  };
  </script>
  
  <style>
  .toggle-switch {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px; /* Adds space between the two buttons */
  }
  
  .toggle-switch input[type="radio"] {
    display: none;
  }
  
  .toggle-switch label {
    cursor: pointer;
    padding: 10px 20px;
    background-color: #f0f0f0;
    border: 2px solid #ccc; /* Makes the border thicker */
    margin: 0;
    transition: background-color 0.3s, color 0.3s, transform 0.3s; /* Smooth transitions */
    border-radius: 20px; /* Rounded corners */
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2); /* Adds a subtle shadow */
  }
  
  .toggle-switch input[type="radio"]:checked + label {
    background-color: #4CAF50; /* A green background for selected */
    color: white;
    transform: scale(1.05); /* Slightly enlarges the selected button */
  }
  
  /* Hover effect */
  .toggle-switch label:hover {
    background-color: #ddd; /* Light grey background on hover */
  }
  
  /* Overlay content styling */
  .overlay-content {
    background-color: #ffffff; /* Ensures the background is white */
    border-radius: 15px; /* Rounded corners for the overlay */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Shadow for the overlay */
  }
  

  .close-button {
  background-color: #3ea5e5; /* A shade of blue for the button */
  color: white;
  border: none;
  border-radius: 20px;
  padding: 10px 20px;
  font-weight: bold;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  transition: background-color 0.3s, transform 0.3s;
}

.close-button:hover {
  background-color: #a2c530; /* Darker shade on hover */
  transform: scale(1.05);
}

.close-button:focus, .close-button:active {
  outline: none;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.chapter-summary {
  margin-bottom: 20px;
  padding: 10px;
  border-bottom: 1px solid #ddd;
  transition: background-color 0.3s, box-shadow 0.3s; /* Smooth transition for hover effects */
}

.chapter-summary:hover {
  background-color: #ffffe0; /* Light yellow background on hover */
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); /* Slight shadow for a "lifted" effect */
}

.chapter-summary h3 {
  font-size: 1.2em;
  color: #333;
  transition: color 0.3s; /* Smooth transition for text color */
}

.chapter-summary h3:hover {
  color: #007bff; /* Change color on hover */
}

.chapter-summary p {
  font-size: 1em;
  color: #666;
}
  </style>
  
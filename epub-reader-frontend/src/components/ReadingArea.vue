<template>
  <div class="reading-area flex flex-col items-center justify-center">
      <!-- if showsummary is not true show book-area -->
      <div id="book-area" class="bg-white shadow-md rounded p-4">
      </div>

      <div v-if="showBookSummary" class="overlay bg-black bg-opacity-100 fixed inset-0 flex justify-center items-center transition-opacity ease-out duration-300">
          <div class="overlay-content bg-white p-6 rounded-lg shadow-xl w-full sm:w-3/4 md:w-1/2">
            
            <!-- Close button and Toggle Switch in the same row -->
            <div class="flex items-center mb-4">
                <!-- Close button with left arrow -->
                <button @click="closeSummary" class="close-btn mr-4 text-white font-semibold py-2 px-4 rounded transition duration-300 ease-in-out">
                    &#8592; <!-- This is a left arrow symbol -->
                </button>

                <!-- Styled Toggle Switch -->
                <div class="toggle-switch">
                    <input type="radio" id="bookSummary" name="summaryType" value="book" v-model="selectedSummaryType">
                    <label for="bookSummary">Book Summary</label>
                    
                    <input type="radio" id="chapterSummary" name="summaryType" value="chapter" v-model="selectedSummaryType">
                    <label for="chapterSummary">Chapter Summaries</label>
                </div>
            </div>

            <div v-if="selectedSummaryType === 'book'" class="book-summary-container">
              <h2 class="book-summary-title">Book Summary for {{ this.bookTitle }}</h2>
              <div class="book-summary-content">
                  <p>{{ this.bookSummary }}</p>
              </div>
            </div>

            <!-- Chapter Summaries -->
            <div v-else-if="selectedSummaryType === 'chapter'">
              <div v-for="summary in chapterSummaries" :key="summary.title" class="chapter-summary">
                <h3>{{ summary.title }}</h3>
                <p>{{ summary.content }}</p>
              </div>
            </div>
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
        book: Object,
        showBookSummary: Boolean,
        bookTitle: String
    },

    data() {
    return {
        selectedSummaryType: "book",
        bookSummary: null,
        // chapterSummaries: [{ 
        //                             title: "Chapter 1 Summary", 
        //                             content: "Chapter 1 summary"
        //                   }, 
        //                   { 
        //                             title: "Chapter 2 Summary", 
        //                             content: "Chapter 2 summary"
        //                   }, 
        //                   { 
        //                             title: "Chapter 3 Summary", 
        //                             content: "Chapter 3 summary"
        //                   }],
        chapterSummaries: null,
    };
  },
    methods: {
        closeSummary() {
            this.$emit("closeSummary"); 
            this.$emit("handleresize");        
        },

        onShowBookSummaryChanged(newValue) {
            if (newValue) {
                console.log("showsummary turned true, ", this.bookTitle);
            }
        },
        
        getBookSummary() {
            const encodedBookTitle = encodeURIComponent(this.bookTitle);

            axios.get(`/book-summary/${encodedBookTitle}`)
                .then(response => {
                    // this.bookSummary = response.data.book_summary;
                    // console.log("the summary from response is", response.data.book_summary)
                    this.bookSummary = response.data.book_summary;
                })
                .catch(error => {
                    console.error("Error fetching book summary:", error);
                    // Handle the error. For example, you might want to show an error message to the user.
                });

            // set the first element of currentSummaries to currentBookSummary
        },

        generateChapterIdentifier(chapterName) {
          // Assuming bookTitle is set when the book is loaded
          // check if chapter name is passed
          if (!chapterName) {
            return `${this.bookTitle}_Chapter_${this.currentChapterURI}`;
          }
          else {
            return `${this.bookTitle}_Chapter_${chapterName}`;
          }
        },

        getChapterSummaries() {
        if (!this.book) {
            console.error("Book not loaded");
            return;
        }
        // if (this.fileUploaded === false) {
        //   console.log('file not uploaded at all')
        //     this.uploadEpubFile();
        // }
        let chapters = this.book.spine.spineItems;
        let summaryPromises = chapters.map(chapter => {
            let chapterId = this.generateChapterIdentifier(chapter.href);
            
            return axios.get(`/chapter-summary/${encodeURIComponent(chapterId)}`)
                .then(response => {
                    if (response.data.status === 'success') {
                        return {
                            title: chapter.href,
                            content: response.data.chapter_summary.summary
                        };
                    } else {
                        console.log('response error response.data.status', response.data.status)
                        return {
                            title: "Chapter Summary for " + chapter.href,
                            content: "Summary is pending for this chapter."
                        };
                    }
                })
                .catch(error => {
                    console.error("Error fetching summary for chapter:", chapter.href, error);
                    return {
                        title: "Chapter Summary for " + chapter.href,
                        content: "An error occurred while fetching the chapter summary."
                    };
                });
        });

        Promise.all(summaryPromises).then(summaries => {
            this.chapterSummaries = summaries;
        });
    },
  
  },
    watch: {
        showBookSummary: function (newValue) {
            // console.log("Show book summary changed to:", newValue);
            this.onShowBookSummaryChanged(newValue);
        },
        selectedSummaryType: function (newValue) {
            console.log("Selected summary type changed for book:", this.bookTitle);
            if (newValue === "book") {
                console.log("Setting current summaries to book summary");
                this.currentSummaries = this.bookSummary;
            } else {
                this.currentSummaries = this.chapterSummaries;
            }
        }
    },


  mounted() {
    
    // call following functions after nexttick
    console.log("Reading area mounted", this.bookTitle);
    this.getBookSummary();
    this.getChapterSummaries();
  }
  };


  </script>
  
  <style>
.close-btn {
    background-color: #007bff; /* Blue background for the button */
    color: white; /* White text color */
    border: none;
    cursor: pointer;
    font-size: 16px; /* Comfortable font size */
    border-radius: 4px; /* Rounded corners */
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Shadow for depth */
    transition: background-color 0.3s, box-shadow 0.3s; /* Smooth transition */
}

.close-btn:hover {
    background-color: #0056b3; /* Darker blue on hover */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15); /* Larger shadow on hover */
}

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
    max-height: 80vh; /* 80% of the viewport height */
    overflow-y: auto; /* enables vertical scrolling */
  }


.chapter-summary {
    background-color: #f8f8f8; /* Light background for each summary */
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Softer shadow for depth */
    margin-bottom: 10px; /* Space between each summary */
    transition: box-shadow 0.3s ease, transform 0.3s ease; /* Smooth transition for hover effects */
}

.chapter-summary:hover {
    box-shadow: 0 5px 10px rgba(0, 0, 0, 0.15); /* Larger shadow on hover for a "lifted" effect */
    transform: translateY(-3px); /* Slightly raise the summary */
}

.chapter-summary h3 {
    color: #333; /* Dark color for the title */
    font-size: 20px; /* Slightly smaller font size than the book summary title */
    margin-bottom: 10px; /* Space between title and content */
}

.chapter-summary p {
    font-size: 16px; /* Comfortable reading font size */
    line-height: 1.6; /* Line height for better readability */
    color: #555; /* Slightly lighter color for the content */
}

.close-button {
    background-color: #007bff; /* Blue background for the button */
    border: none;
    cursor: pointer;
    display: inline-block;
    margin-top: 20px; /* Space above the button */
}

.close-button:hover {
    background-color: #0056b3; /* Darker blue on hover for visual feedback */
}

.book-summary-container {
    background-color: #f8f8f8; /* Light background for the container */
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Soft shadow for depth */
    margin-top: 20px;
    transition: box-shadow 0.3s ease, transform 0.3s ease; /* Smooth transition for hover effects */

}

.book-summary-container:hover {
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2); /* Larger shadow on hover for a "lifted" effect */
    transform: translateY(-5px); /* Slightly raise the container */
}

.book-summary-title {
    color: #333; /* Dark color for the title */
    font-size: 24px; /* Larger font size for the title */
    margin-bottom: 15px; /* Space between title and content */
}

.book-summary-content {
    font-size: 16px; /* Comfortable reading font size */
    line-height: 1.6; /* Line height for better readability */
    color: #555; /* Slightly lighter color for the content */
}
  </style>
  
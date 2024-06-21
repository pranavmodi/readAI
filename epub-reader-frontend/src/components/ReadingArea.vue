<template>
    <div class="reading-area flex flex-col items-center justify-center">
        <!-- if showsummary is not true show book-area -->
        <div id="book-area" class="bg-white shadow-md rounded p-4"></div>
  
        <!-- Chat Interface Overlay -->
    <!-- Chat Interface Overlay -->
        <div v-if="showChat" class="chat-overlay bg-black bg-opacity-50 fixed inset-0 flex justify-end items-start transition-opacity ease-out duration-300" style="pointer-events: none;">
            <div 
                class="chat-container bg-white p-4 rounded-lg shadow-xl w-full sm:w-1/3 md:w-1/4 h-3/4 mt-12 mr-4 resize overflow-auto" 
                :style="{ top: chatPosition.top, right: chatPosition.right, position: 'absolute', pointerEvents: 'auto' }"
                @mousedown="startDrag">
                <div class="chat-header flex justify-between items-center p-2 rounded-t-lg cursor-move">
                <h2 class="text-lg font-semibold">Chat with Book AI</h2>
                <button @click="closeChat" class="text-xl">&#10005;</button> <!-- Close button -->
                </div>
                <div class="chat-messages flex-1 overflow-y-auto p-2" style="max-height: calc(100% - 80px);">
                <!-- Messages will be displayed here -->
                <div v-for="message in messages" :key="message.id" :class="{'self-end bg-blue-300': message.is_user, 'self-start bg-gray-300': !message.is_user}" class="chat-message p-2 rounded my-1 max-w-3/4">
                    {{ message.text }}
                </div>
                </div>
                <div class="chat-input w-full p-2 flex items-center">
                <input v-model="newMessage" @keyup.enter="sendMessage" type="text" placeholder="Type a message..." class="w-full p-2 rounded border-2 border-gray-300">
                <button @click="sendMessage" class="p-2 bg-blue-500 text-white rounded">Send</button>
                <div v-if="isLoading" class="spinner"></div> <!-- Loading spinner -->
                </div>
            </div>
        </div>
  
        <div v-if="showBookSummary" class="overlay bg-black bg-opacity-100 fixed inset-0 flex justify-center items-center transition-opacity ease-out duration-300">
            <div class="overlay-content bg-white p-6 rounded-lg shadow-xl w-full sm:w-3/4 md:w-1/2">
                <div class="flex flex-col w-full">
                    <!-- Progress Bar -->
                    <div v-if="showProgressBar" class="progress-bar-container mb-4">
                        <p class="progress-text">Summaries are being generated, please wait...</p>
                        <div class="progress-bar" :style="{ width: progress + '%' }"></div>
                    </div>
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

                    <!-- Book Summary -->
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
        </div>
  
        <!-- Other buttons and functionality specific to reading a book -->
        <div class="button-group space-x-2">
            <!-- Buttons for navigation, font size adjustment, etc. -->
        </div>
    </div>
</template>
  
<script>
import { io } from 'socket.io-client';
import axios from 'axios';
axios.defaults.baseURL = 'http://localhost:8000/';

export default {
    props: {
        book: Object,
        showBookSummary: Boolean,
        bookTitle: String,
        showChat: Boolean,
        filename: String
    },

    data() {
        return {
            selectedSummaryType: "book",
            bookSummary: null,
            chapterSummaries: null,
            messages: [],
            newMessage: '',
            isDragging: false,
            dragStartX: 0,
            dragStartY: 0,
            chatPosition: { top: '12rem', right: '1rem' },
            chatStartTop: 0,
            chatStartRight: 0,
            showProgressBar: false,
            progress: 0,
            isLoading: false
        };
    },
    methods: {
        async checkProcessingStatus(filename) {
            try {
                const response = await fetch(`http://localhost:8000/status-epub?filename=${filename}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }

                const statusResult = await response.json();
                return statusResult.status;

            } catch (error) {
                console.error("Error checking processing status:", error);
                return 'error';
            }
        },

        checkSummaryGeneration() {
            this.showProgressBar = true;
            const socket = io('http://localhost:8000');

            // Move the fetch API call outside the connect event handler
            console.log('this.filename', this.filename)
            fetch('http://localhost:8000/process-epub', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ filename: this.filename })  // Adjust payload as necessary
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Book processing initiated:', data);
            })
            .catch(error => {
                console.error('Error in book processing:', error);
            });

            socket.on('connect', () => {
                console.log('Connected to server, ready to receive updates');
            });

            socket.on('progress_update', (data) => {
                this.progress = data.progress;
            });

            socket.on('disconnect', () => {
                console.log('Disconnected from server');
                this.showProgressBar = false;
                this.getBookSummary();
                this.getChapterSummaries();
            });

            console.log("End of checkSummaryGeneration!!! ");
        },

        async sendMessage() {
            if (!this.newMessage.trim()) return;  // Prevent sending empty messages

            this.isLoading = true; // Show the loading spinner

            // Change the file extension from .epub to .npy
            const npy_path = this.filename.replace(/\.epub$/, '.npy');
            const json_name = this.filename.replace(/\.epub$/, '.json');

            // Construct the user message
            const userMessage = {
                id: Date.now(),  // Unique ID for the message
                text: this.newMessage,
                is_user: true
            };

            // Push the user message to the messages array
            this.messages.push(userMessage);

            // Clear the input field
            this.newMessage = '';

            // Make API call to chat_with_book endpoint
            try {
                const response = await axios.post('/chat_with_book', {
                query: userMessage.text,
                npy_path: npy_path,  // Use the new filename with .npy extension
                json_name: json_name
                });

                const aiResponse = {
                id: Date.now(),
                text: response.data.response,
                is_user: false
                };

                // Push the AI response to the messages array
                this.messages.push(aiResponse);

                // Optional: Scroll to the bottom of the chat view
                this.$nextTick(() => {
                const container = this.$el.querySelector(".chat-messages");
                container.scrollTop = container.scrollHeight;
                });
            } catch (error) {
                console.error("Error during chat_with_book API call:", error);
                // Optionally, handle the error by showing an error message in the chat
                const errorResponse = {
                id: Date.now(),
                text: "Error during chat_with_book API call. Please try again later.",
                is_user: false
                };
                this.messages.push(errorResponse);
            } finally {
                this.isLoading = false; // Hide the loading spinner
            }
        },

        startDrag(event) {
            this.isDragging = true;
            this.dragStartX = event.clientX;
            this.dragStartY = event.clientY;
            this.chatStartTop = parseFloat(this.chatPosition.top);
            this.chatStartRight = parseFloat(this.chatPosition.right);
            document.addEventListener('mousemove', this.drag);
            document.addEventListener('mouseup', this.stopDrag);
        },

        stopDrag() {
            this.isDragging = false;
            document.removeEventListener('mousemove', this.drag);
            document.removeEventListener('mouseup', this.stopDrag);
        },

        drag(event) {
            if (this.isDragging) {
                const deltaX = event.clientX - this.dragStartX;
                const deltaY = event.clientY - this.dragStartY;
                // Convert the start position and delta into pixels and adjust accordingly
                this.chatPosition.right = `${this.chatStartRight - deltaX}px`;
                this.chatPosition.top = `${this.chatStartTop + deltaY}px`;
            }
        },

        closeChat() {
            this.$emit("closeChat"); 
        },

        closeSummary() {
            this.$emit("closeSummary"); 
            this.$emit("handleresize");        
        },

        getBookSummary() {
            const encodedBookTitle = encodeURIComponent(this.bookTitle);
            console.log("the book title", this.bookTitle);

            axios.get(`/book-summary/${encodedBookTitle}`)
                .then(response => {
                    this.bookSummary = response.data.book_summary;
                })
                .catch(error => {
                    console.error("Error fetching book summary:", error);
                });
        },

        generateChapterIdentifier(chapterName) {
            if (!chapterName) {
                return `${this.bookTitle}_Chapter_${this.currentChapterURI}`;
            } else {
                return `${this.bookTitle}_Chapter_${chapterName}`;
            }
        },

        getChapterSummaries() {
            if (!this.book) {
                console.error("Book not loaded");
                return;
            }
            let chapters = this.book.spine.spineItems;
            let summaryPromises = chapters.map(chapter => {
                let chapterId = this.generateChapterIdentifier(chapter.href);
                
                return axios.get(`/chapter-summary/${encodeURIComponent(chapterId)}`)
                    .then(response => {
                        if (response.data.status === 'success') {
                            return {
                                title: response.data.chapter_summary.title,
                                content: response.data.chapter_summary.summary
                            };
                        } else {
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
            if (newValue) {
                this.checkSummaryGeneration();
            }
        },
        selectedSummaryType: function (newValue) {
            if (newValue === "book") {
                this.currentSummaries = this.bookSummary;
            } else {
                this.currentSummaries = this.chapterSummaries;
            }
        }
    },

    mounted() {
        console.log("Reading area mounted", this.bookTitle);
    }
};
</script>

<style scoped>
.chat-container {
    resize: both; /* Makes the container resizable */
    overflow: auto; /* Adds a scrollbar if content overflows */
    position: absolute;
}

.chat-header {
    background-color: #f34c4c; /* Lighter background for the header */
    cursor: move; /* Indicates draggable area */
}

.chat-messages {
    max-height: calc(100% - 100px); /* Adjust this value based on header and input heights */
    overflow-y: auto; /* Adds a vertical scrollbar if content overflows */
}

.chat-messages::-webkit-scrollbar {
    width: 10px;
}

.chat-messages::-webkit-scrollbar-thumb {
    background-color: darkgrey;
    border-radius: 10px;
}

.chat-messages::-webkit-scrollbar-track {
    background: #f1f1f1;
}

.chat-input {
    margin-right: 8px; /* Space between the input field and the send button */
    flex-grow: 1; /* Allows the input field to fill the space */
}

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

.toggle-switch label:hover {
    background-color: #ddd; /* Light grey background on hover */
}

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

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left-color: #22a6b3;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 1s linear infinite;
  margin-left: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>

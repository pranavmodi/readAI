# Use an official Node runtime as a parent image
FROM node:lts

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json (or yarn.lock)
COPY package*.json ./

# Install project dependencies
RUN npm install

# Bundle app source
COPY . .

# Make port 8080 available outside this container
EXPOSE 8080

# Define the command to run the app
CMD ["npm", "run", "serve"]


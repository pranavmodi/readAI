# Use a Node.js base image to build Tailwind CSS
FROM node:latest as build-stage

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock)
# COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of your app's source code
COPY . /app

# Build the Tailwind CSS (assuming a build script is defined in package.json)
RUN npm run build

# Use Nginx to serve the static content
FROM nginx:stable-alpine as production-stage

# Copy static assets from builder stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx when the container launches
CMD ["nginx", "-g", "daemon off;"]
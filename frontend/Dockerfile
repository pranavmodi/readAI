# Step 1: Use a Node.js base image
FROM node:latest as build-stage

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy package.json and package-lock.json
COPY package*.json ./

# Step 4: Install dependencies
RUN npm install

# Step 5: Copy project files and folders to the working directory
COPY . .

# Step 6: Build the project for production
RUN npm run build

# Step 7: Use Nginx to serve the static files
FROM nginx:stable-alpine as production-stage

# Step 8: Copy built assets from build-stage to Nginx
COPY --from=build-stage /app /usr/share/nginx/html

# Step 9: Expose port 80
EXPOSE 80

# Step 10: Start Nginx server
CMD ["nginx", "-g", "daemon off;"]

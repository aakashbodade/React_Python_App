# Step 1: Use a Node.js base image for building
FROM node:16 AS build

# Set working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the app's code into the container
COPY . .

# Build the React application
RUN npm run build

# Step 2: Use a lightweight web server to serve the app
FROM nginx:alpine

# Copy built React files from the "build" stage to Nginx's web root
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80 for the web server
EXPOSE 80

# Start the Nginx server
CMD ["nginx", "-g", "daemon off;"]
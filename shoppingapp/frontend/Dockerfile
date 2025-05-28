# Step 1: Use a Node.js base image for building
FROM node:16 AS build

# Set working directory inside the container
WORKDIR /app

# Copy package files first (for better Docker layer caching)
COPY shoppingapp/frontend/package.json /app/package.json
COPY shoppingapp/frontend/package-lock.json /app/package-lock.json

# Install dependencies
RUN npm install

# Copy the rest of the frontend application files
COPY shoppingapp/frontend/public/ /app/public/
COPY shoppingapp/frontend/src/ /app/src/

# Build the React application
RUN npm run build

# Step 2: Use a lightweight web server to serve the app
FROM nginx:alpine

# Copy built React files from the "build" stage to Nginx's web root
# React builds to 'build' directory, not 'Build'
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80 for the web server
EXPOSE 80

# Start the Nginx server
CMD ["nginx", "-g", "daemon off;"]
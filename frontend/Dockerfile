### STAGE 1: Build the React application ###
# We use Node.js 20, as required by your project's tools (Vite)
FROM node:20-alpine as build

WORKDIR /app

# Copy package files and install all dependencies, including react-select
COPY package*.json ./
RUN npm install

# Copy the rest of the frontend source code
COPY . .

# Build the application for production
RUN npm run build

### STAGE 2: Serve the built application with Nginx ###
FROM nginx:stable-alpine

# Copy the static files from the 'build' stage to the Nginx server directory
COPY --from=build /app/dist /usr/share/nginx/html

# This ensures that routing within your React app works correctly
COPY --from=build /app/dist/index.html /usr/share/nginx/html/index.html

# Expose port 80 for the Nginx server
EXPOSE 80

# The default command for the Nginx image will start the server
CMD ["nginx", "-g", "daemon off;"]


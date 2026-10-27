FROM nginx:alpine

# Copy nginx configuration
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Expose ports
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

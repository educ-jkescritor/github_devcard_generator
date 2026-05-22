FROM nginx:alpine

# Copy index.html to a template location
COPY index.html /usr/share/nginx/html/index.html.template

# Default backend URL
ENV BACKEND_URL=http://localhost:8080

# Use envsubst to replace the variable and start nginx
CMD ["/bin/sh", "-c", "envsubst '${BACKEND_URL}' < /usr/share/nginx/html/index.html.template > /usr/share/nginx/html/index.html && exec nginx -g 'daemon off;'"]

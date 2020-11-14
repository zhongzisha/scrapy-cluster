docker pull nginx
docker run -d -p 8081:80 --name website -v `pwd`/../simple_website:/usr/share/nginx/html nginx
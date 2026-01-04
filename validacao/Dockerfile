FROM eclipse-temurin:21-jdk-alpine
WORKDIR /app
COPY src ./src
RUN cd src && javac *.java
EXPOSE 6000
CMD ["java", "-cp", "src", "ServidorRMI"]
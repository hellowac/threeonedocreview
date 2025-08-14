# Use the official OpenJDK 8 Alpine image
FROM openjdk:8-jdk-alpine3.7

# Set the working directory inside the container
WORKDIR /app

# Copy the JAR file into the container at /app
COPY ./acloud-isc-token-server-1.5.1-20201126.054109-1.jar /app/acloud-isc-token-server-1.5.1-20201126.054109-1.jar

COPY ./application.yml /app/application.yml
COPY ./bootstrap.yml /app/bootstrap.yml

# Define the command to run the JAR file when the container starts
CMD ["java", "-jar", "acloud-isc-token-server-1.5.1-20201126.054109-1.jar", "--spring.config.location=application.yml", "--spring.config.location=bootstrap.yml"]
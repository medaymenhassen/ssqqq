#!/bin/bash

# Script to set up both Django and Spring Boot applications with shared PostgreSQL database

echo "Setting up shared database configuration..."

# Check if database-config.json exists
if [ ! -f "database-config.json" ]; then
    echo "Error: database-config.json not found!"
    exit 1
fi

echo "Loading database configuration..."
CONFIG=$(cat database-config.json)

# Extract values from JSON
DB_HOST=$(echo $CONFIG | jq -r '.host')
DB_PORT=$(echo $CONFIG | jq -r '.port')
DB_USER=$(echo $CONFIG | jq -r '.user')
DB_PASSWORD=$(echo $CONFIG | jq -r '.password')
DB_NAME=$(echo $CONFIG | jq -r '.database')

echo "Database configuration loaded:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  User: $DB_USER"
echo "  Database: $DB_NAME"

# Create database if it doesn't exist (requires psql to be installed)
echo "Checking if database exists..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME
if [ $? -ne 0 ]; then
    echo "Creating database $DB_NAME..."
    PGPASSWORD=$DB_PASSWORD createdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME
    if [ $? -eq 0 ]; then
        echo "Database $DB_NAME created successfully!"
    else
        echo "Failed to create database $DB_NAME"
        exit 1
    fi
else
    echo "Database $DB_NAME already exists."
fi

echo "Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Start Django application: cd assistance && python manage.py runserver"
echo "2. Start Spring Boot application: cd School && mvn spring-boot:run"
echo "3. Start Angular application: cd 3Dproject && npm start"